import java.io.*;
import org.antlr.runtime.*;
import org.antlr.runtime.debug.DebugEventSocketProxy;


public class __Test__ {

    public static void main(String args[]) throws Exception {
        SCodeLexer lex = new SCodeLexer(new ANTLRFileStream("/Volumes/JetDrive/Dev/Sheridan/EnvironMUD/environmock/output/__Test___input.txt", "UTF8"));
        CommonTokenStream tokens = new CommonTokenStream(lex);

        SCodeParser g = new SCodeParser(tokens, 49100, null);
        try {
            g.text_adventure();
        } catch (RecognitionException e) {
            e.printStackTrace();
        }
    }
}