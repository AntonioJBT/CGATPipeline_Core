import cpgReport


##########################################################################
##########################################################################


class rnaseqTSSOverlapSummary(cpgReport.cpgTracker):

    '''Summary table'''
    mPattern = "_rnaseq_tss_venn$"

    def __call__(self, track, slice=None):
        query = '''SELECT track, intervals FROM %(track)s_rnaseq_tss_venn'''
        data = self.getAll(query)
        return data

##########################################################################


class ensemblGeneTSSOverlapSummary(cpgReport.cpgTracker):

    '''Summary table'''
    mPattern = "_ensembl_gene_tss_venn$"

    def __call__(self, track, slice=None):
        query = '''SELECT track, intervals FROM %(track)s_ensembl_gene_tss_venn'''
        data = self.getAll(query)
        return data
