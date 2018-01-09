      subroutine sub
      Use mod_toto
      Use mod_titi

      Integer :: b

      b = cte*2
      write(*,*) "b = ", b
      end subroutine sub