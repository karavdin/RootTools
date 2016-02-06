def getCTypeString(typeString):
    '''Translate ROOT shortcuts for branch description to proper C types
    '''
    if typeString in cStringTypeDict.keys():
        return cStringTypeDict[typeString]
    else:
        raise Exception( "Cann ot determine C type for type '%s'"%typeString )

def getCDefaultString(typeString):
    '''Get default string from ROOT branch description shortcut
    '''
    if typeString in defaultTypeDict.keys():
        return defaultTypeDict[typeString]
    else:
        raise Exception( "Can not determine C type for type '%s'"%typeString )

def createClassString(scalars, vectors, useSTDVectors = False):
    '''Create class string from scalar and vector variables
    '''
    scalarDeclaration = "".join(["  %s %s;\n"% ( getCTypeString(scalar['type']), scalar['name'] ) for scalar in scalars])
    scalarInitString  = "".join(["  %s = %s;\n"%( scalar['name'], getCDefaultString(scalar['type']) ) for scalar in scalars]) 
    vectorDeclaration = ""
    vectorInitString  = ""
    if useSTDVectors:
        for vector in vectors:
            vectorDeclaration += "".join([ "  std::vector< %s > %s_%s;\n" % \
                ( getCTypeString(c['type']), vector['name'], c['name']) for c in vector['variables']])
            vectorInitString  += "".join([ "  %s_%s.clear();\n" % \
                ( vector['name'], c['name']) for c in vector['variables']])
    else:
        for vector in vectors:
            assert vector.has_key('nMax'), "Vector definition needs nMax if using C arrays: %r"%vector
            vectorDeclaration += "".join([ "  %s %s_%s[%3i];\n" % \
                ( getCTypeString(c['type']), vector['name'], c['name'], vector['nMax']) for c in vector['variables']])
            vectorInitString  += """  for(UInt_t i=0;i<{nMax};i++){{\n{vecCompString}     }}; //End for loop"""\
                .format(nMax = vector['nMax'], vecCompString =\
                 "".join([ "  %s_%s[i] = %15s;\n"%(vector['name'], c['name'], getCDefaultString(c['type'])) for c in vector['variables']]) 
            )

    return \
"""#ifndef __className__
#define __className__

#include<vector>
#include<TMath.h>


class className{{
  public:
{scalarDeclaration}
{vectorDeclaration}
  void init(){{

{scalarInitString}
{vectorInitString}
  }}; // End init
}}; // End class declaration
#endif""".format(scalarDeclaration = scalarDeclaration,\
                 scalarInitString = scalarInitString, vectorDeclaration=vectorDeclaration, 
                 vectorInitString=vectorInitString)
