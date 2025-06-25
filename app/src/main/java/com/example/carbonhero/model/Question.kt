package com.example.carbonhero.model

sealed class Question {
    data class SingleChoice(
        val question: String,
        val options: List<String>,
        val fieldName: String
    ) : Question()

    data class MultipleChoice(
        val question: String,
        val options: List<String>,
        val fieldName: String
    ) : Question()

    data class TextInput(
        val question: String,
        val fieldName: String
    ) : Question()

    data class YesNo(
        val question: String,
        val fieldName: String
    ) : Question()
} 