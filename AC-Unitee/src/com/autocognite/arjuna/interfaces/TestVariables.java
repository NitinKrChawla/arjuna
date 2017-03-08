package com.autocognite.arjuna.interfaces;

import java.util.Map;

import com.autocognite.pvt.batteries.value.DefaultStringKeyValueContainer;

public interface TestVariables {

	TestObjectProperties objectProps() throws Exception;

	TestProperties testProps() throws Exception;

	StringKeyValueContainer customProps() throws Exception;

	StringKeyValueContainer udv() throws Exception;

	ReadOnlyDataRecord dataRecord();

	DataReference dataRef(String refName) throws Exception;
	
	Map<String, DataReference> getAllDataReferences();

}