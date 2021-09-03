/**
 * 
 */
package cognitiveservices;

import com.azure.ai.textanalytics.TextAnalyticsAsyncClient;
import com.azure.core.credential.AzureKeyCredential;
import com.azure.ai.textanalytics.models.*;
import com.azure.ai.textanalytics.TextAnalyticsClientBuilder;
import com.azure.ai.textanalytics.TextAnalyticsClient;

import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.TimeUnit;

import java.util.Arrays;
import com.azure.core.util.Context;
import com.azure.core.util.polling.SyncPoller;
import com.azure.ai.textanalytics.util.AnalyzeHealthcareEntitiesResultCollection;
import com.azure.ai.textanalytics.util.AnalyzeHealthcareEntitiesPagedIterable;

/**
 * @author Marton Marek
 *
 */
public class TextAnalytics {
	
	private static String KEY = "d1d53d61a7c74854b70ad40e77519499";
    private static String ENDPOINT = "https://sierracognitive.cognitiveservices.azure.com/";
    
    static TextAnalyticsClient client = authenticateClient(KEY, ENDPOINT);
	
    //establish connection to a client
    private static TextAnalyticsClient authenticateClient(String key, String endpoint) {
        return new TextAnalyticsClientBuilder()
            .credential(new AzureKeyCredential(key))
            .endpoint(endpoint)
            .buildClient();
    }
    
    /**
	 * sentiment analysis returns 4 strings as follows:
	 * 1. Sentiment Summary [Positive, Neutral, Negative]
	 * 2. Positive Score [0.0 - 1.0]
	 * 3. Neutral Score [0.0 - 1.0]
	 * 4. Negative Score [0.0 - 1.0]
	 */
    static String[] documentSentimentAnalysis(String text) {

		String [] list = new String[4];

	    DocumentSentiment documentSentiment = client.analyzeSentiment(text);
	    
	    list[0] = documentSentiment.getSentiment().toString();
	    list[1] = String.valueOf(documentSentiment.getConfidenceScores().getPositive());
	    list[2] = String.valueOf(documentSentiment.getConfidenceScores().getNeutral());
	    list[3] = String.valueOf(documentSentiment.getConfidenceScores().getNegative());
	    
	    return list;
	}
    
    static String[] sentenceSentimentAnalysis(String text) {

		String [] list = new String[4];

	    DocumentSentiment documentSentiment = client.analyzeSentiment(text);
	    
	    list[0] = documentSentiment.getSentiment().toString();
	    list[1] = String.valueOf(documentSentiment.getConfidenceScores().getPositive());
	    list[2] = String.valueOf(documentSentiment.getConfidenceScores().getNeutral());
	    list[3] = String.valueOf(documentSentiment.getConfidenceScores().getNegative());
	    
	    
	    for (SentenceSentiment sentenceSentiment : documentSentiment.getSentences()) {
	        System.out.printf(
	            "Recognized sentence sentiment: %s, positive score: %s, neutral score: %s, negative score: %s.%n",
	            sentenceSentiment.getSentiment(),
	            sentenceSentiment.getConfidenceScores().getPositive(),
	            sentenceSentiment.getConfidenceScores().getNeutral(),
	            sentenceSentiment.getConfidenceScores().getNegative());
	    }
	    
	    return list;
	}
	
	//Returns only the sentiment summary 
	static String sentimentAnalysisSummary(String text) {
		
		String summary = new String();

	    DocumentSentiment documentSentiment = client.analyzeSentiment(text);
	    
	    summary = documentSentiment.getSentiment().toString();
	    
	    return summary;

	}
	
	
	
	static void opinionMining(String document) {

	     AnalyzeSentimentOptions options = new AnalyzeSentimentOptions().setIncludeOpinionMining(true);
	     final DocumentSentiment documentSentiment = client.analyzeSentiment(document, "en", options);
	     SentimentConfidenceScores scores = documentSentiment.getConfidenceScores();
	     
	     System.out.printf(
	             "Recognized document sentiment: %s, positive score: %f, neutral score: %f, negative score: %f.%n",
	             documentSentiment.getSentiment(), scores.getPositive(), scores.getNeutral(), scores.getNegative());


	     documentSentiment.getSentences().forEach(sentenceSentiment -> {
	         SentimentConfidenceScores sentenceScores = sentenceSentiment.getConfidenceScores();
	         System.out.printf("\tSentence sentiment: %s, positive score: %f, neutral score: %f, negative score: %f.%n",
	                 sentenceSentiment.getSentiment(), sentenceScores.getPositive(), sentenceScores.getNeutral(), sentenceScores.getNegative());
	         
	         sentenceSentiment.getOpinions().forEach(opinion -> {
	             TargetSentiment targetSentiment = opinion.getTarget();
	             System.out.printf("\t\tTarget sentiment: %s, target text: %s%n", targetSentiment.getSentiment(),
	                     targetSentiment.getText());
	             
	             for (AssessmentSentiment assessmentSentiment : opinion.getAssessments()) {
	                 System.out.printf("\t\t\t'%s' assessment sentiment because of \"%s\". Is the assessment negated: %s.%n",
	                         assessmentSentiment.getSentiment(), assessmentSentiment.getText(), assessmentSentiment.isNegated());
	             }
	         });
	     });
	 }

}
