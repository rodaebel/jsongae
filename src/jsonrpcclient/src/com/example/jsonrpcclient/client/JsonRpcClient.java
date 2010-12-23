package com.example.jsonrpcclient.client;

import com.google.gwt.core.client.EntryPoint;
import com.google.gwt.event.dom.client.ClickEvent;
import com.google.gwt.event.dom.client.ClickHandler;
import com.google.gwt.http.client.Request;
import com.google.gwt.http.client.RequestBuilder;
import com.google.gwt.http.client.RequestCallback;
import com.google.gwt.http.client.RequestException;
import com.google.gwt.http.client.Response;
import com.google.gwt.json.client.JSONArray;
import com.google.gwt.json.client.JSONException;
import com.google.gwt.json.client.JSONNull;
import com.google.gwt.json.client.JSONNumber;
import com.google.gwt.json.client.JSONObject;
import com.google.gwt.json.client.JSONParser;
import com.google.gwt.json.client.JSONString;
import com.google.gwt.json.client.JSONValue;
import com.google.gwt.user.client.Window;
import com.google.gwt.user.client.rpc.AsyncCallback;
import com.google.gwt.user.client.ui.Button;
import com.google.gwt.user.client.ui.Label;
import com.google.gwt.user.client.ui.RootPanel;


/**
 * Entry point class.
 */
public class JsonRpcClient implements EntryPoint {
	protected final String service_endpoint;

	private int JSONRequestID;

	public JsonRpcClient() {
		this.service_endpoint = "/rpc";
		this.JSONRequestID = 0;
	}

	protected final void makeRPC(String methodName, JSONArray params, final AsyncCallback<JSONValue> cb) {
		JSONObject requestData = new JSONObject();
		requestData.put("method", new JSONString(methodName));
		requestData.put("params", params);
		requestData.put("jsonrpc", new JSONString("2.0"));
		requestData.put("id", new JSONNumber(JSONRequestID++));

		RequestBuilder rb = this.createBuilder();

		try {
			rb.sendRequest(requestData.toString(), new RequestCallback() {
				public void onError(Request request, Throwable exception) {
					cb.onFailure(exception);
				}

				public void onResponseReceived(Request request, Response response) {
					String text = response.getText();
					if (text == null || text.equals("")) {
						throw new JSONException("JSON-RPC response body from server was empty");
					} 
					JSONObject jsonResponse = (JSONObject) JSONParser.parseStrict(text);

					// Test if compatible JSON-RPC Response
					if ((jsonResponse.containsKey("error") || jsonResponse.containsKey("result")) &&
						!jsonResponse.containsKey("id")
					) {
						throw new JSONException("No JSON-RPC response from server");
					} else {
						JSONValue error = jsonResponse.get("error");
						if (error != null && !(error instanceof JSONNull)) {
							throw new JSONException(error.toString());
						}

						cb.onSuccess(jsonResponse.get("result"));
					}
				}
			});

		} catch (RequestException e) {
			cb.onFailure(e);
		} catch(JSONException e) {
			cb.onFailure(e);
		} catch(Exception e) {
			System.out.println(e);
			cb.onFailure(e);
		}
	}
	
	protected final void makeRPC(String methodName, JSONArray params) {
		JSONObject requestData = new JSONObject();
		requestData.put("method", new JSONString(methodName));
		requestData.put("params", params);
		requestData.put("jsonrpc", new JSONString("2.0"));

		RequestBuilder rb = this.createBuilder();

		try {
			rb.sendRequest(requestData.toString(), new RequestCallback() {
				public void onError(Request request, Throwable exception) {
					Window.alert(exception.toString());
				}

				public void onResponseReceived(Request request, Response response) {
					// Notifications don't get responses.
				}
			});
		} catch(Exception e) {
			System.out.println(e);
		}
	}

	protected RequestBuilder createBuilder() {
		RequestBuilder result = new RequestBuilder(RequestBuilder.POST, this.service_endpoint);
		result.setHeader("Content-type", "application/json; charset=utf-8");

		return result;
	}

	// UI Elements

	private Label label = new Label();

	public void setLabel(String data) {
		this.label.setText(data.toString());
	}

	public void onModuleLoad() {
		// Assemble the root panel.

		Button fetchButton = new Button("Fetch");
		fetchButton.addClickHandler(new ClickHandler() {
			
			@Override
			public void onClick(ClickEvent event) {
				// Update data.
				JSONArray params = new JSONArray();
				params.set(0, new JSONString("foobar"));
				makeRPC("data", params, new AsyncCallback<JSONValue>() {

					@Override
					public void onSuccess(JSONValue result) {
						setLabel("JSON-RPC result: " + result.toString());
					}

					@Override
					public void onFailure(Throwable caught) {
						Window.alert(caught.toString());
					}
				});
			}
		});

		Button notifyButton = new Button("Notify");
		notifyButton.addClickHandler(new ClickHandler() {

			@Override
			public void onClick(ClickEvent event) {
				// Update data.
				JSONArray params = new JSONArray();
				params.set(0, new JSONString("A notification"));
				params.set(1, new JSONNumber(10));
				makeRPC("notify", params);
			}
		});

		RootPanel.get("appContainer").add(fetchButton);
		RootPanel.get("appContainer").add(notifyButton);
		RootPanel.get("appContainer").add(label);
	}
}
