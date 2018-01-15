(import [asyncio [get-event-loop]]
        [asyncitertools :as op]
        [functools [partial]]
        [threading [current-thread]]
        [time [sleep]])


(defmacro Σ [stream &rest body]
  `(for/a [it ~stream] ~@body))


(defmacro with-executor [loop &rest body]
  `(.run-in-executor loop None (fn* [] ~@body)))


(defn mapper [loop value]
  (with-executor loop
    (setv thread-name (. (current-thread) name))
    (print (.format "Processing {} on thread {}" value thread_name))
    (sleep 3)
    value))


(defn/a main [loop]
  (Σ (->> (op.from-iterator (range 40))
          (op.flat-map (partial mapper loop)))
     (print it)))


(defmain [&rest args]
  (setv loop (get-event-loop))
  (.run-until-complete loop (main loop)))
