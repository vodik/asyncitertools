(import [asyncio [ensure-future get-event-loop sleep]]
        [tkinter [Frame Label TclError Tk]]
        [observer [Observer]]
        [asyncitertools :as op])


(defmacro λ [&rest body]
  `(fn [it] ~@body))


(defmacro forever [&rest body]
  `(while True ~@body))


(defn/a position-label [label idx events]
  (for/a [ev (->> events
                  (op.delay (/ idx 20)))]
    (.place label
            :x (+ ev.x (* idx 10) 15)
            :y ev.y)))


(defn/a main [&optional [loop None]]
  (setv mousemoves (Observer)
        root (Tk)
        frame (Frame :width 800 :height 600))

  (.title root "asyncitertools (hy)")
  (.bind frame "<Motion>" (λ (ensure-future (.send mousemoves it))))

  (setv tasks [])
  (for [[idx char] (enumerate "TIME FLIES LIKE AN ARROW")]
    (setv label (Label frame :text char))
    (.config label {"borderwidth" 0 "padx" 0 "pady" 0})
    (.append tasks (ensure-future (position-label label idx mousemoves))))

  (.pack frame)
  (try
    (forever (.update root) (await (sleep 0.005)))
    (except [e TclError]
      (if (not (in "application has been destroyed" (. e args [0])))
          (raise)))
    (finally
      (for [task tasks] (.cancel task))))


(defmain [&rest args]
  (.run-until-complete (get-event-loop) (main)))
