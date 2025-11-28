from unittest.mock import MagicMock, patch
from src.services.ai_service import analyze_image_pro

@patch("google.generativeai.GenerativeModel")
@patch("google.generativeai.configure")
@patch("src.services.ai_service.find_best_model_dynamic")
def test_analyze_image_pro_success(mock_find_model, mock_configure, mock_model_class):
    # Setup mock
    mock_find_model.return_value = ("gemini-pro", None)
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance

    mock_response = MagicMock()
    mock_response.text = '{"is_furniture": true}'
    mock_model_instance.generate_content.return_value = mock_response

    # Call
    image = MagicMock()
    result_json, model_name = analyze_image_pro(image, 5000, "fake_key")

    # Assert
    assert result_json == '{"is_furniture": true}'
    assert model_name == "gemini-pro"
    mock_configure.assert_called_with(api_key="fake_key")
    # Verify find_best_model_dynamic was called with the key
    mock_find_model.assert_called_with("fake_key")

@patch("src.services.ai_service.find_best_model_dynamic")
def test_analyze_image_pro_no_key(mock_find_model):
    result_json, error = analyze_image_pro(None, 5000, None)
    assert result_json is None
    assert error == "Clé API manquante"

@patch("google.generativeai.GenerativeModel")
@patch("google.generativeai.configure")
@patch("src.services.ai_service.find_best_model_dynamic")
def test_analyze_image_pro_api_error(mock_find_model, mock_configure, mock_model_class):
    # Setup mock
    mock_find_model.return_value = ("gemini-pro", None)
    mock_model_instance = MagicMock()
    mock_model_class.return_value = mock_model_instance

    # Simulate API Error
    mock_model_instance.generate_content.side_effect = Exception("API Error")

    # Call
    image = MagicMock()
    result_json, error = analyze_image_pro(image, 5000, "fake_key")

    # Assert
    assert result_json is None
    assert "API Error" in error
