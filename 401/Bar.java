//////////////////////////////////////////////////////////////
// Bar.java

public class Bar
{
  public void doSomething(Foo x)
  {
    // This switch statement produce anonymous inner class Bar$1.
    switch (x)
      {
      case A:
      case B:
      default:
      }
  }
}
