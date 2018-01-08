;; Example running an aiohttp server doing search queries against
;; Wikipedia to populate the autocomplete dropdown in the web UI. Start
;; using `python autocomplete.py` and navigate your web browser to
;; http://localhost:8080
;; 
;; Requirements:
;; * aiohttp
;; * aiohttp_jinja2

(import [os]
        [json]
        [asyncio]
        [aiohttp [ClientSession WSMsgType web]]
        [aiohttp.web [Application WebSocketResponse]]
        [aiohttp_jinja2]
        [asyncitertools :as op]
        [jinja2 [FileSystemLoader]])


(defmacro λ [&rest body]
  `(fn [it] ~@body))


(defmacro Λ [&rest body]
  `(fn/a [it] ~@body))


(def *wikipedia-url* "http://en.wikipedia.org/w/api.php")


(defn/a search-wikipedia [term]
  (setv params {"action" "opensearch"
                "search" term
                "format" "json"})

  (with/a [session (ClientSession)
           resp (.get session *wikipedia-url* :params params)]
    (await (.text resp))))


(defn/a websocket-handler [request]
  (setv ws (WebSocketResponse))
  (await (.prepare ws request))

  (defn/a read-ws []
    (for/a [msg ws]
      (cond
        [(= msg.type WSMsgType.TEXT)
         (yield (json.loads msg.data))]
        [(= msg.type WSMsgType.ERROR)
         (print (.format "ws connection closed with exception" (.exception ws)))
         (break)])))

  (await
    (->> (read-ws)
         (op.map (λ (.rstrip (get it "term"))))
         (op.filter (λ (> (len it) 2)))
         (op.debounce 0.5)
         (op.distinct-until-changed)
         (op.map search-wikipedia)
         (op.subscribe (Λ (await (.send-str it result))))))
  ws)


(with-decorator
  (aiohttp_jinja2.template "index.html")
  (defn/a index [request] {}))


(defn init [&optional [loop None]]
  (setv app (doto (Application :loop loop)
                  (.router.add-static "/static" "static")
                  (.router.add-get "/" index)
                  (.router.add-get "/ws" websocket-handler)))

  (aiohttp_jinja2.setup app :loader (FileSystemLoader "."))
  app)


(defmain [&rest args]
  (setv loop (asyncio.get-event-loop))
  (web.run-app (init :loop loop) :host "localhost" :port 8080))
