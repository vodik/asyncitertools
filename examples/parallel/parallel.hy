(import [asyncio [get-event-loop]]
        [asyncitertools :as op])


(defmacro with-executor [&rest body]
  `(do
     (import [asyncio [get-event-loop]])
     (.run-in-executor (get-event-loop) None (fn* [] ~@body))))


(defn mapper [value]
  (import [threading [current-thread]]
          [time [sleep]])

  (with-executor
    (setv thread-name (. (current-thread) name))
    (print (.format "Processing {} on thread {}" value thread_name))
    (sleep 3)
    value))


(defn/a main []
  (setv stream (->> (op.from-iterator (range 40))
                    (op.flat-map mapper)))

  (for/a [value stream] (print value)))


(defmain [&rest args]
  (.run-until-complete (get-event-loop) (main)))
