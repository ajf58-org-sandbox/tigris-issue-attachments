import java.util.Date;
import java.util.Comparator;

public class Foo
{
  public void foo()
  {
    Comparator<Date> comp = new Comparator<Date>()
      {
        static final long serialVersionUID = 1L;
        public int compare(Date lhs, Date rhs)
        {
          return 0;
        }
      };
  }
}
