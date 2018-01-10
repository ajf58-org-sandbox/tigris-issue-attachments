//////////////////////////////////////////////////////////////
// Foo.java

public enum Foo
{
  A, B;

  public void doSomething()
  {
    // This switch statement produce anonymous inner class Foo$1.
    switch(this)
      {
      case A:
      case B:
      default:
      }
  }
}
