/**
 * 
 */
package cognitiveservices;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileWriter;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Iterator;
import java.util.List;
import java.util.NoSuchElementException;
import java.util.Optional;
import java.util.Queue;
import java.util.Scanner;

import com.zavtech.morpheus.frame.DataFrame;
import com.zavtech.morpheus.frame.DataFrameRow;

/**
 * @author Marton Marek
 *
 */
public class Data {
	
	public Data() {
		
	}
	
	/**
	 * Takes the current folder (execution folder) and runs analysis on every .txt file 
	 */
	public void transcriptFileAnalysis() {
		
		ArrayList<String> list = new ArrayList<String>();
		
		//get the current path
		try {
			String currentPath = new java.io.File(".").getCanonicalPath();
			
			File folder = new File(currentPath);
			
			//get all files
			list = listFiles(folder);
			
			//if we have files in the list
			if (list.size() > 0) {
				Iterator<String> iter = list.iterator();
				
				//iterate through each file 
				while (iter.hasNext()) {
					analyseText(iter.next());
				}
			}
				
		} catch (IOException e) {
			// TODO Auto-generated catch block
			e.printStackTrace();
		}
	
	}
	
	/**
	 * Adds 4 sentiment columns to the given twitter data file
	 * 1. sentiment summary 2. positive 3. neutral 4. negative 
	 * Output file is "tweetresult.csv"
	 * @param file
	 */
	
	public void twitterFullSentiment(String file) {
		
		System.out.println("Running tweet analysis through cognitive services...");
		
		ArrayDeque<String> summaryResults = new ArrayDeque<String>();
		ArrayDeque<String> positiveResults = new ArrayDeque<String>();
		ArrayDeque<String> neutralResults = new ArrayDeque<String>();
		ArrayDeque<String> negativeResults = new ArrayDeque<String>();
		
		DataFrame.read().csv(options -> {
		    options.setResource(file);
		    //options.setExcludeColumnIndexes(0);
		}).cols().add("sentiment_summary", String.class, v -> {
		    String tweet = v.row().getValue("clean_tweet");
		    
		    summaryResults.add(TextAnalytics.documentSentimentAnalysis(tweet)[0]);
		    positiveResults.add(TextAnalytics.documentSentimentAnalysis(tweet)[1]);
		    neutralResults.add(TextAnalytics.documentSentimentAnalysis(tweet)[2]);
		    negativeResults.add(TextAnalytics.documentSentimentAnalysis(tweet)[3]);

		    return summaryResults.pop();
		}).cols().add("positive", String.class, v -> {
			
		    return positiveResults.pop();
		}).cols().add("neutral", String.class, v -> {

		    return neutralResults.pop();
		}).cols().add("negative", String.class, v -> {

		    return negativeResults.pop();
		}).rows().sort(false, "sentiment_summary").write().csv(options -> {
		    options.setFile("tweetresult.csv");
		    options.setTitle("DataFrame");
		}); 
		
		System.out.println("Successfully written results to tweetresult.csv");
	
	}
	
	
	/**
	 * Adds only the summary sentiment to the given twitter file
	 * Tweet must be under column name "tweet"
	 * Output file is "tweetsummary.csv"
	 * @param file
	 */
	public void twitterSummarySentiment(String file) {
		
		DataFrame.read().csv(options -> {
		    options.setResource(file);
		    //options.setExcludeColumnIndexes(0);
		}).cols().add("sentiment_summary", String.class, v -> {
		    String tweet = v.row().getValue("tweet");

		    return TextAnalytics.sentimentAnalysisSummary(tweet);
		}).rows().sort(false, "sentiment_summary").write().csv(options -> {
		    options.setFile("tweetsummary.csv");
		    options.setTitle("DataFrame");
		});
	
	}
	
	
	/**
	 * Helper function that outputs txt file analysis to csv files
	 * @param filename
	 */
	private void analyseText(String filename) {
		
		System.out.println("Running transcript analysis through cognitive services...");
		
		File file = new File(filename);

		Path path = Paths.get("transcript_results.csv");
		Path summaryPath = Paths.get("transcript_summary.csv");
		
		
		try {
			Scanner scan = new Scanner(file);
			
			scan.useDelimiter("\\*\\*");
		
			
			FileWriter writer; 
			FileWriter summary;
			
			if (!Files.exists(path)) {
				//write the headers
				writer = new FileWriter("transcript_results.csv", true);
				writer.write("date,segment,sentiment,positive,neutral,negative\n");
			}
			else {
				writer = new FileWriter("transcript_results.csv", true);
			}
			
			if (!Files.exists(summaryPath)) {
				//write the headers
				summary = new FileWriter("transcript_summary.csv", true);
				summary.write("date,positive,neutral,negative\n");
			}
			else {
				summary = new FileWriter("transcript_summary.csv", true);
			}
			
			while (scan.hasNext()) {
			
				String text = scan.next();
				
				if (!text.isBlank()) {
				
					String[] result = text.split("\n", 2);
					
					if (!result[0].isBlank() && !result[1].isBlank()) {
						
						//calculate how many segments there are in the transcript (1 segment = 5000 characters)
						double numOfSegments = Math.ceil((double)result[1].length() / (double)5000);
						
						//used to keep track of the average results of each transcript
						double totalPositive = 0.0;
						double totalNeutral = 0.0;
						double totalNegative = 0.0;
												
						//loop through the number of segments
						for (int i = 0; i < numOfSegments; i++) {
							//calculate starting offset
							int offset = i * 5000;
							
							//create substring of the current segment
							String subString = result[1].substring(offset, Math.min(result[1].length(), offset + 5000));
							
							//analyse the substring
							String[] sentiment = TextAnalytics.documentSentimentAnalysis(subString);
							
							//write the result to a file			
							writer.write(result[0].trim() + "," 
															+ (i + 1) + ","  // records the segment number starting at 1
															+ sentiment[0] + ","
															+ sentiment[1] + ","
															+ sentiment[2] + ","
															+ sentiment[3] + ","												
															+ "\n");
							
							totalPositive += Double.parseDouble(sentiment[1]);
							totalNeutral += Double.parseDouble(sentiment[2]);
							totalNegative += Double.parseDouble(sentiment[3]);

						}
						
						//write summary to the file
						summary.write(result[0].trim() + "," 
								+ totalPositive / numOfSegments + ","
								+ totalNeutral / numOfSegments + ","
								+ totalNegative / numOfSegments 									
								+ "\n");

					}
				}
			}
			
			writer.close();
			summary.close();
			
		} catch (FileNotFoundException e) {
			System.out.println("File not found!");
		} catch (IOException e) {
	    	System.out.println("Error writing to the file!");
		} catch (ArrayIndexOutOfBoundsException ae) {
			System.out.println("Problem with input file");
		}
		
		System.out.println("Successfully wrote results from file - " + filename + " to results.csv");
				
	}
	
	/**
	 * Helper Function that looks for .txt files in a given folder
	 * @param folder
	 * @return
	 */
	private ArrayList<String> listFiles(final File folder) {
		//stores the name of each file 
		ArrayList<String> list = new ArrayList<String>();
		
	    for (final File fileEntry : folder.listFiles()) {
	    	
	    	//ignore directories 
	    	if (!fileEntry.isDirectory()) {
	    		
	    		try {
		    		String extension = getExtension(fileEntry.getName()).get();
		        	if (extension.equals("txt")) {
		        		list.add(fileEntry.getName());
		        	}
	    		}
	    		catch (NoSuchElementException ne) {
	    			System.out.println("No .txt files exist in this folder!");
	    		}
	        }
	    }
	    
	    return list;
	    
	}
	
	
	private Optional<String> getExtension(String filename) {
	    return Optional.ofNullable(filename)
	      .filter(f -> f.contains("."))
	      .map(f -> f.substring(filename.lastIndexOf(".") + 1));
	}

}
