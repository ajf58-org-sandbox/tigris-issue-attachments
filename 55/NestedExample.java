import java.util.*;

public class NestedExample
{
	public NestedExample()
	{
		Thread t = new Thread() {
			public void start()
			{
				Thread t = new Thread() {
					public void start()
					{
						try {Thread.sleep(200);}
						catch (Exception e) {}
					}
				};
				while (true)
				{
					try {Thread.sleep(200);}
					catch (Exception e) {}
				}
			}
		};
	}


	public static void main(String argv[])
	{
		NestedExample e = new NestedExample();
	}
}
