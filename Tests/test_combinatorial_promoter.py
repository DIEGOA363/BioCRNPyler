
# this file made by Andrey Shur, 5/5/2020
# copyright something or other

from unittest import TestCase
import warnings
class TestCombinatorialPromoter(TestCase):
    def test_initialization(self):
        from biocrnpyler import CombinatorialPromoter, Protein, Species, Combinatorial_Cooperative_Binding
        #initializing with one regulator that has no list
        newprom = CombinatorialPromoter("testprom","treg1")
        self.assertTrue(newprom.regulators == [Species("treg1",material_type="protein")])
        #initializing with a list of strings
        newprom2 = CombinatorialPromoter("testprom",["treg1","treg2"])
        #it should convert strings into proteins
        self.assertTrue(newprom2.regulators == [Species("treg1",material_type="protein"),
                                                Species("treg2",material_type="protein")])
        #by default, all complexes are tx capable
        print(newprom2.tx_capable_list)
        self.assertTrue(newprom2.tx_capable_list==[{"treg1"},{"treg2"},{"treg1","treg2"}])

        #you should be able to define a tx_capable_list
        newprom3 = CombinatorialPromoter("testprom",["treg1","treg2"],\
                                    tx_capable_list=[["treg1","treg2"],["treg2"]])
        
        self.assertTrue(newprom3.tx_capable_list==[{"treg1","treg2"},{"treg2"}])

        #if you define it with a species in the regulators it should work
        newprom4 = CombinatorialPromoter("testprom",["treg1",Species("treg2",material_type="rna")])
        print(newprom4.tx_capable_list)
        self.assertTrue(newprom4.tx_capable_list == [{"treg1"},{"treg2"},{"treg1","treg2"}])
        self.assertTrue(newprom4.regulators == [Species("treg1",material_type="protein"),
                                                Species("treg2",material_type="rna")])
        #make sure the default mechanism is the correct one
        self.assertTrue(isinstance(newprom4.default_mechanisms["binding"],Combinatorial_Cooperative_Binding))
    def test_update_species(self):
        from biocrnpyler import CombinatorialPromoter, Protein, Species, Combinatorial_Cooperative_Binding, \
                                    DNAassembly,Transcription_MM, Translation_MM, Multimer, ComplexSpecies
        #make a complicated promoter
        newprom = CombinatorialPromoter("testprom",["treg1",Species("treg2",material_type="rna")],\
                                tx_capable_list = [["treg1","treg2"]],cooperativity={"testprom_treg2":1},leak=True)
        newdna = DNAassembly("testDNA",promoter=newprom)
        newdna.update_mechanisms(mechanisms={"transcription":Transcription_MM(), "translation":Translation_MM()})
        newdna.update_parameters(parameters={"cooperativity":2,"kb":100, "ku":10, "ktx":.05, "ktl":.2, "kdeg":2})
        newprom_spec = newprom.update_species()

        sp_treg1 = Species("treg1",material_type="protein")
        sp_treg2 = Species("treg2",material_type="rna")
        #mu_treg2 = Multimer(sp_treg2,2)

        sp_dna = Species("testDNA",material_type="dna")
        sp_rnap = Species("RNAP",material_type="protein")
        sp_rna = Species("testDNA",material_type="rna")
        cp_dna_rnap = ComplexSpecies([sp_dna,sp_rnap])
        cp_dna_treg1 = ComplexSpecies([sp_dna,sp_treg1,sp_treg1])
        cp_dna_treg2 = ComplexSpecies([sp_dna,sp_treg2])
        cp_dna_treg1_rnap = ComplexSpecies([cp_dna_treg1,sp_rnap])
        cp_dna_treg2_rnap = ComplexSpecies([cp_dna_treg2,sp_rnap])
        cp_dna_treg1_treg2 = ComplexSpecies([sp_dna,sp_treg1,sp_treg1,sp_treg2])
        cp_dna_treg1_treg2_rnap = ComplexSpecies([cp_dna_treg1_treg2,sp_rnap])

        knownspecies = [sp_dna,sp_rnap,sp_rna,cp_dna_rnap,cp_dna_treg1,\
                            cp_dna_treg2,cp_dna_treg1_treg2,cp_dna_treg1_rnap, \
                                cp_dna_treg2_rnap,cp_dna_treg1_treg2_rnap]

        #these are the species that should come out
        test_set = set([str(a) for a in newprom_spec])
        mistake_found = False
        #we should have the correct length of species
        self.assertTrue(len(test_set)==len(knownspecies))
        for known_spec in knownspecies:
            #go through and check each species if it's in the set generated by the promoter
            if(str(known_spec) not in test_set):
                print("couldn't find "+str(known_spec))
                mistake_found = True
                break
        self.assertTrue(not mistake_found)

        
    def test_update_reactions(self):
        """this function tests the CombinatorialPromoter for the ability to make
        reactions with the proper inputs and outputs."""
        from biocrnpyler import CombinatorialPromoter, Protein, Species, Combinatorial_Cooperative_Binding, \
                                    DNAassembly,Transcription_MM, Translation_MM, ComplexSpecies, Multimer
        
        #make a relatively simple combinatorial promoter
        newprom = CombinatorialPromoter("testprom",["treg1","treg2"],tx_capable_list=[["treg2","treg1"]])
        #you have to put it into an assembly
        newdna = DNAassembly("testDNA",promoter=newprom)
        #adding mechanisms because there is no mixture. I believe this is what the mixture does
        newdna.update_mechanisms(mechanisms={"transcription":Transcription_MM(), "translation":Translation_MM()})
        newdna.update_parameters(parameters={"cooperativity":2,"kb":100, "ku":10, "ktx":.05, ("testprom_leak","ktx"):.01,\
                                                                ("testprom_leak","ku"):50,("testprom_treg1_treg2_RNAP","ku"):5})
        #you have to do update_species first
        newprom_spec = newprom.update_species()
        #now the test... does it produce the right reactions??
        newprom_rxns = newprom.update_reactions()
        #here i am generating the species manually
        sp_dna = Species("testDNA",material_type="dna")
        sp_rna = Species("testDNA",material_type="rna")
        sp_treg1 = Species("treg1",material_type="protein")
        sp_treg2 = Species("treg2",material_type="protein")
        sp_rnap = Species("RNAP",material_type="protein")
        #now the complexes
        
        sp_dna_treg1 = ComplexSpecies([sp_dna,sp_treg1,sp_treg1])
        sp_dna_treg2 = ComplexSpecies([sp_dna,sp_treg2,sp_treg2])
        sp_dna_treg1_treg2 = ComplexSpecies([sp_dna,sp_treg2,sp_treg2,sp_treg1,sp_treg1])
        sp_dna_rnap = ComplexSpecies([sp_dna,sp_rnap])
        sp_dna_treg1_rnap = ComplexSpecies([sp_dna_treg1,sp_rnap])
        sp_dna_treg2_rnap = ComplexSpecies([sp_dna_treg2,sp_rnap])
        sp_dna_treg1_treg2_rnap = ComplexSpecies([sp_dna_treg1_treg2,sp_rnap])
        #print('\n\n'.join([str(a) for a in newprom_rxns]))
        #now, we generate the reaction input outputs manually
        r0 = [set([sp_rnap,sp_dna]),set([sp_dna_rnap]),100,50] #RNAP binding to DNA
        r1 = [set([sp_dna_rnap]),set([sp_dna,sp_rna,sp_rnap]),.01,0] #leaky transcription
        r2 = [set([sp_dna,sp_treg1]),set([sp_dna_treg1]),100,10] #treg1 binding
        r3 = [set([sp_dna_treg1,sp_rnap]),set([sp_dna_treg1_rnap]),100,50] #rnap binding to treg1 bound dna
        r4 = [set([sp_dna_treg1_rnap]),set([sp_dna_treg1,sp_rnap,sp_rna]),.01,0] #leaky tx from single regulator
        r5 = [set([sp_dna_treg2_rnap]),set([sp_dna_treg2,sp_rnap,sp_rna]),.01,0] #leaky tx from single regulator
        r6 = [set([sp_dna_treg1_treg2_rnap]),set([sp_dna_treg1_treg2,sp_rnap,sp_rna]),.05,0] #ktx for regular tx
        r7 = [set([sp_dna_treg2,sp_rnap]),set([sp_dna_treg2_rnap]),100,50] #rnap binding to treg2 bound dna
        r8 = [set([sp_dna,sp_treg2]),set([sp_dna_treg2]),100,10] #treg2 binding
        r9 = [set([sp_dna_treg1,sp_treg2]),set([sp_dna_treg1_treg2]),100,10] #treg2 binding to dna that already has treg1
        r10 = [set([sp_dna_treg2,sp_treg1]),set([sp_dna_treg1_treg2]),100,10] #treg1 binding to dna that already has treg2
        r11 = [set([sp_dna_treg1_treg2,sp_rnap]),set([sp_dna_treg1_treg2_rnap]),100,5] #rnap binding to full complex
        truthlist = [r0,r1,r2,r3,r4,r5,r6,r7,r8,r9,r10,r11]
        #print('\n\n'.join([str(a) for a in newprom_rxns]))
        for rxn in newprom_rxns:
            in_outs = [set(rxn.inputs),set(rxn.outputs)]
            correctPick = False
            for rset in truthlist:
                #go through all the reactions and make sure that
                #they have the correct inputs, outputs, and constants.
                if(rset[0]==in_outs[0] and rset[1] == in_outs[1]):
                    self.assertTrue(rxn.k==rset[2])
                    self.assertTrue(rxn.k_r==rset[3])
                    correctPick = True
                    break

            self.assertTrue(correctPick)
        #12 reactions must be generated
        self.assertTrue(len(newprom_rxns)==len(truthlist))
        #TODO: tests below this are questionable
        #then we should also test what happens if you say that nothing can transcribe:
        newprom2 = CombinatorialPromoter("testprom",["treg1"])#,tx_capable_list = [])
        newdna2 = DNAassembly("testDNA",promoter=newprom2)
        #adding mechanisms because there is no mixture. I believe this is what the mixture does
        newdna2.update_mechanisms(mechanisms={"transcription":Transcription_MM(), "translation":Translation_MM()})
        newdna2.update_parameters(parameters={"cooperativity":2,"kb":100, "ku":10, "ktx":.05})
        with self.assertWarns(UserWarning):
            #TODO fix this with a warning detection system that actually checks for the proper warning
            newprom_rxns = newprom2.update_reactions()
