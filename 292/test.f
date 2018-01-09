      Module mod_toto
      Integer :: i,a
      End Module mod_toto

      Module mod_titi
      Integer, PARAMETER :: cte=3
      End Module mod_titi

      Module mod_tata
      PUBLIC
      Contains
      Include "test_inc.f"
      End Module mod_tata


      program test
      use mod_toto
      use mod_titi
      use mod_tata

      i=5
      a = i + cte
      write(*,*) "a =", a
      CALL sub

      end program test