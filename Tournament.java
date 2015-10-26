package tournament;
import java.util.*;
import myUtils.*;

class Tournament  {
	ArrayList <Contender> conList;
	ArrayList <Contender> winList;
	ArrayList <Contender> outList;
	Contender con1;
	Contender con2;
	final int maxLosses = 2;
	boolean finished;
	
	Tournament(String contendersText) {
		conList = new ArrayList <Contender> ();
		winList = new ArrayList <Contender> ();
		outList = new ArrayList <Contender> ();
		finished = false;
		ArrayList <String> lines =
			TextList.arrayListFromStringBlock(contendersText);
		for (String s : lines) {
			conList.add(new Contender(s));
		}
		Collections.shuffle(conList);
		con1 = conList.remove(0);
		con2 = conList.remove(0);
	}
	
	ArrayList <String> getPairs() {
		ArrayList <String> pairs = 
			new ArrayList <String> ();
		pairs.add(con1.name);
		pairs.add(con2.name);
		return pairs;
	}

	String makeChoice(String choice) {
		TextList rvTL = new TextList();
		if (choice.equals("A")) {
			rvTL.add(con1.name);
			rvTL.add("   over");
			rvTL.add(con2.name);
			con1.incrWins();
			con2.incrLosses();
			winList.add(con1);						
			if (con2.lossCount >= maxLosses) {
				outList.add(0,con2);							
			} else {
				winList.add(con2);
			}
		}
		if (choice.equals("B")) {			
			rvTL.add(con2.name);
			rvTL.add("   over");
			rvTL.add(con1.name);
			con2.incrWins();
			con1.incrLosses();
			winList.add(con2);
			if (con1.lossCount >= maxLosses) {
				outList.add(0,con1);
			} else {
				winList.add(con1);
			}
		}
		if (choice.equals("Both")) {
			rvTL.add("Both:");
			rvTL.add("    "+con1.name);
			rvTL.add("    "+con2.name);
			con1.incrWins();
			winList.add(con1);
			con2.incrWins();
			winList.add(con2);
		}
		if (choice.equals("Neither")) {
			rvTL.add("Neither:");
			rvTL.add("    "+con1.name);
			rvTL.add("    "+con2.name);
			con1.incrLosses();
			if (con1.lossCount >= maxLosses) {
				outList.add(0,con1);
			} else {
				winList.add(con1);
			}
			con2.incrLosses();
			if (con2.lossCount >= maxLosses) {
				outList.add(0,con2);
			} else {
				winList.add(con2);
			}			
		}
		if (conList.size()>=2) {
			con1 = conList.remove(0);
			con2 = conList.remove(0);
		} else {
			if (conList.size()==1)
				winList.add(conList.remove(0));
			// now conList.size()==0
			if (winList.size()>=2) {
				// move winners to conList and shuffle
				conList.addAll(winList);
				winList = new ArrayList <Contender> ();
				Collections.shuffle(conList);
				con1 = conList.remove(0);
				con2 = conList.remove(0);				
			} else {
				// winList.size() is 0 or 1
				finished = true;
			}
		}
		return rvTL.toText();
	}
	
	String getStatus() {
		String rv = "running";
		if (finished) {
			rv = "finished";
		}
		return rv;
	}
	
	String getResult() {
		// move contenders from outList to winList
		winList.addAll(outList);
		outList = new ArrayList <Contender> ();		
		// sort by number of wins
		CompareContender cc = new CompareContender();
		Collections.sort(winList,cc);
		// [rank]. ([no. of wins],[no. of losses]) [ContenderName]
		TextList resultsTL = new TextList();
		int rank = 0; 
		for (int i = winList.size()-1;i>=0;i--) {
			Contender c = winList.get(i);
			rank++;
			String line = rank+". ("+c.winCount+","+c.lossCount+") "+c.name;
			resultsTL.add(line);
		}
		return resultsTL.toText();
	}
}
