/**
 * 
 */
package cognitiveservices;


/**
 * @author Marton Marek
 *
 */
public class Main {

	/**
	 * @param args
	 */
	public static void main(String[] args) {
		Data df = new Data();
		
		try {

			if (args.length == 0) {
				System.out.println("Must include parameters as follows: \n"
						+ "-t <twitter csv file> OR \n"
						+ "-s to run transcript analysis in current folder (must contain .txt files)");
			}
			else if (args[0].equals("-t")) {
				df.twitterFullSentiment(args[1]);
			}
			else if (args[0].equals("-s") ) {
				df.transcriptFileAnalysis();
			}
			else if (args[0].equals("-o")) {
				//opinion mining 
				
			}
			else {
				throw new Exception();
			}
			
		}
		catch (Exception e) {
			System.out.println("Must include parameters as follows: \n"
					+ "-t <twitter csv file> OR \n"
					+ "-s to run transcript analysis in current folder (must contain .txt files)");
		}

	}
	
}


