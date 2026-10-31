---
{
  "schema_version": 1,
  "id": "control-failsafe-redundancy",
  "title": "Failsafe и резервирование",
  "language": "ru",
  "section": "05-control-links",
  "type": "concept",
  "summary": "Failsafe задаёт действие при определённом условии отказа; резервирование требует анализа общих элементов и фактического переключения.",
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
    "px4-safety-v116",
    "px4-integrated-gcs"
  ],
  "formula_ids": []
}
---
# Failsafe и резервирование

## Назначение и краткий ответ

Failsafe задаёт действие при определённом условии отказа; резервирование требует анализа общих элементов и фактического переключения.

## Контекст и объяснение

PX4 v1.16, разделы Manual Control Loss Failsafe и Data Link Loss Failsafe, описывает отдельные условия, задержки и действия. Документация PX4 Integrated Ground Control Stations, раздел Failsafes, указывает, что общий MAVLink-радиоканал может привести к одновременному срабатыванию обеих проверок.

## Практическое применение

Документируйте источники команд, общие питание и антенны, критерий потери, тайм-аут, выбранное действие и режим. Проверяйте ожидаемые переходы на стенде и в соответствии с документацией конкретной системы до использования.

## Ограничения и типичные ошибки

Два приёмника, подключённые к общему питанию или одному контроллеру, не устраняют все общие точки отказа. Действия и допустимость настроек нельзя обобщать на все аппараты.

## Связанные материалы и источники

[Основы радиосвязи](../01-radio-fundamentals/index.md); [распространение](../02-wave-propagation/index.md). Источники: [PX4 v1.16 Safety](https://docs.px4.io/v1.16/en/config/safety), Manual Control Loss Failsafe и Data Link Loss Failsafe; [PX4 Integrated Ground Control Stations](https://docs.px4.io/main/en/config/integrated_gcs), Failsafes, версия main меняется и должна быть сверена с установленной прошивкой. Статья — черновик и ожидает технического ревью.
