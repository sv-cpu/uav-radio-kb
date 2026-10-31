---
{
  "schema_version": 1,
  "id": "control-fhss-dsss",
  "title": "5.5 FHSS и DSSS: принципы и ограничения",
  "language": "ru",
  "section": "05-control-links",
  "type": "concept",
  "summary": "FHSS изменяет частоту по последовательности; DSSS применяет расширяющую последовательность к данным. Оба названия описывают семейства методов, а не конкретный протокол.",
  "tags": [
    "control"
  ],
  "aliases": [],
  "status": "draft",
  "created_at": "2026-10-31",
  "updated_at": "2026-10-31",
  "reviewed_at": null,
  "review_due": null,
  "verification": {
    "sources": "pending",
    "formulas": "not_applicable",
    "technical_review": "pending",
    "review_record": null
  },
  "rag": {
    "include": false
  },
  "related": [],
  "sources": [
    "adi-spread-spectrum"
  ],
  "formula_ids": []
}
---
# 5.5 FHSS и DSSS: принципы и ограничения

## Назначение и краткий ответ

FHSS изменяет частоту по последовательности; DSSS применяет расширяющую последовательность к данным. Оба названия описывают семейства методов, а не конкретный протокол.

## Контекст и объяснение

Analog Devices, An Introduction to Spread-Spectrum Communications, раздел Different Modulation Spreading Techniques, различает применение последовательности к данным и к частоте несущей; последующие подразделы обсуждают DSSS и FHSS. Для работы приёмник должен согласованно обрабатывать соответствующую последовательность и режим.

## Практическое применение

При изучении документированной системы записывайте версию протокола, частотный план, режим, скорость и условия измерения. Не выводите параметры конкретного изделия из общего названия метода.

## Ограничения и типичные ошибки

Расширение спектра не является доказательством шифрования, аутентификации или гарантированной устойчивости к любой помехе. Требования к спектру определяются конкретной юрисдикцией и режимом.

## Связанные материалы и источники

[Основы радиосвязи](../01-radio-fundamentals/index.md); [распространение](../02-wave-propagation/index.md). Источник: [adi-spread-spectrum](https://www.analog.com/en/resources/technical-articles/introduction-to-spreadspectrum-communications--maxim-integrated.html), Different Modulation Spreading Techniques, DSSS и FHSS. Статья — черновик и ожидает технического ревью.
