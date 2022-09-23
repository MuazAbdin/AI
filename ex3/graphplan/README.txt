300575297
314977638
*****
======================
Q13-14: TOWER OF HANOI
======================
TO automatically create domain and problem files for of the Tower of Hanoi problem
for any number of disks and pegs, we followed this PDDL description of the problem,
as it found in many sources, (i.e. https://web-planner.herokuapp.com/)

; Domain description
; Describe the relations and transitions that can occur
; This one describes the Tower of Hanoi puzzle
(define (domain hanoi) ; Domain name must match problem's

  ; Define what the planner must support to execute this domain
  ; Only domain requirements are currently supported
  (:requirements
    :strips                 ; basic preconditions and effects
    :negative-preconditions ; to use not in preconditions
    :equality               ; to use = in preconditions
    ; :typing               ; to define type of objects and parameters
  )

  ; Define the relations
  ; Question mark prefix denotes free variables
  (:predicates
    (clear ?x)      ; An object ?x is clear
    (on ?x ?y)      ; An object ?x is on object ?y
    (smaller ?x ?y) ; An object ?x is smaller than object ?y
  )

  ; Define a transition to move a disc from one place to another
  (:action move
    :parameters (?disc ?from ?to)
    ; Only conjunction or atomic preconditions are supported
    :precondition (and
      (smaller ?disc ?to)
      (smaller ?disc ?from)
      (on ?disc ?from)
      (clear ?disc)
      (clear ?to)
      (not (= ?from ?to)) ; Negative precondition and equality
    )
    ; Only conjunction or atomic effects are supported
    :effect (and
      ; Note that adding the new relations is not enough
      (clear ?from)
      (on ?disc ?to)
      ; Remove the old relations, order is not important
      (not (on ?disc ?from))
      (not (clear ?to))
    )
  )

  ; Other transitions can be defined here
)

; Problem description
; Describe one scenario within the domain constraints
; This one describes the Tower of Hanoi with 3 discs
(define (problem pb3)
  (:domain hanoi)

  ; Objects are candidates to replace free variables
  (:objects peg1 peg2 peg3 d1 d2 d3)

  ; The initial state describe what is currently true
  ; Everything else is considered false
  (:init
    ; Discs are smaller than pegs
    (smaller d1 peg1) (smaller d1 peg2) (smaller d1 peg3)
    (smaller d2 peg1) (smaller d2 peg2) (smaller d2 peg3)
    (smaller d3 peg1) (smaller d3 peg2) (smaller d3 peg3)
    ; Discs are also smaller than some other discs
    (smaller d1 d2) (smaller d1 d3)
    (smaller d2 d3)

    ; There is nothing on top of some pegs and disc
    (clear peg2)
    (clear peg3)
    (clear d1)

    ; Discs are stacked on peg1
    (on d3 peg1)
    (on d2 d3)
    (on d1 d2)
  )

  ; The goal state describe what we desire to achieve
  (:goal (and
    ; Discs stacked on peg3
    (on d3 peg3)
    (on d2 d3)
    (on d1 d2)
  ))
)