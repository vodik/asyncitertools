(import [asyncio [get-event-loop]]
        [asyncitertools :as op]
        [functools [partial]]
        [threading [current-thread]]
        [time [sleep]])


(defmacro λ/a [&rest body]
  `(fn/a [it] ~@body))


(defmacro with-executor [loop &rest body]
  `(.run-in-executor loop None (fn* [] ~@body)))


(defn mapper [loop value]
  (with-executor loop
    (setv thread-name (. (current-thread) name))
    (print (.format "Processing {} on thread {}" value thread_name))
    (sleep 3)
    value))


(defn/a main [loop]
  (await (->> (op.from-iterator (range 40))
              (op.flat-map (partial mapper loop))
              (op.subscribe (λ/a (print it))))))


(defmain [&rest args]
  (setv loop (get-event-loop))
  (.run-until-complete loop (main loop)))
