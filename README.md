# Django Production-Ready Authentication System

A robust, reusable, and secure authentication component for Django projects using Django Rest Framework (DRF). This system is designed to be "plug-and-play" and follows market standards for security and user experience.

## 🚀 Features

- **Custom User Model:** Email-based login (instead of username).
- **Secure Signup:** 2-step registration with Email OTP verification.
- **Login Security:** Account lockout mechanism (locks for 15 minutes after 3 failed attempts).
- **JWT Authentication:** Secure Access and Refresh tokens using `simplejwt`.
- **Password Management:** Secure "Forgot Password" flow with OTP verification.
- **API First:** Fully decoupled REST APIs ready for React, Vue, or Mobile Apps.
- **Scalable:** Built as a standalone app (`authentication`) for easy integration.

## 🛠 Tech Stack

- Python 3.x
- Django 4.x / 5.x
- Django Rest Framework (DRF)
- Simple JWT

---

## 📦 Installation Guide

Follow these steps to integrate this component into any Django project.

### 1. Prerequisites
Install the required libraries:
```bash
pip install djangorestframework djangorestframework-simplejwt
