import { Injectable } from '@angular/core';
import * as CryptoJS from 'crypto-js';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class CryptoService {
  private readonly secretKey = environment.encryptionKey;

  constructor() { }

  /**
   * Encrypt data using AES-256-CBC with random IV
   */
  encrypt(data: string): string {
    try {
      const iv = CryptoJS.lib.WordArray.random(16);
      const encrypted = CryptoJS.AES.encrypt(data, this.secretKey, {
        iv: iv,
        mode: CryptoJS.mode.CBC,
        padding: CryptoJS.pad.Pkcs7
      });
      
      // Combine IV and encrypted data
      const combined = iv.concat(encrypted.ciphertext);
      return combined.toString(CryptoJS.enc.Base64);
    } catch (error) {
      console.error('Encryption failed:', error);
      throw new Error('Failed to encrypt data');
    }
  }

  /**
   * Decrypt data using AES-256-CBC
   */
  decrypt(encryptedData: string): string {
    try {
      const combined = CryptoJS.enc.Base64.parse(encryptedData);
      const iv = CryptoJS.lib.WordArray.create(combined.words.slice(0, 4));
      const ciphertext = CryptoJS.lib.WordArray.create(combined.words.slice(4));
      
      const decrypted = CryptoJS.AES.decrypt(
        { ciphertext: ciphertext } as any,
        this.secretKey,
        {
          iv: iv,
          mode: CryptoJS.mode.CBC,
          padding: CryptoJS.pad.Pkcs7
        }
      );
      
      return decrypted.toString(CryptoJS.enc.Utf8);
    } catch (error) {
      console.error('Decryption failed:', error);
      throw new Error('Failed to decrypt data');
    }
  }

  /**
   * Generate JWT-like token structure (without actual JWT signing)
   */
  generateToken(username: string): string {
    const payload = {
      username,
      iat: Math.floor(Date.now() / 1000),
      exp: Math.floor(Date.now() / 1000) + (24 * 60 * 60), // 24 hours
      iss: 'lora-dashboard',
      sub: username
    };
    
    return this.encrypt(JSON.stringify(payload));
  }

  /**
   * Verify and decode token
   */
  verifyToken(token: string): { username: string; exp: number } | null {
    try {
      const decrypted = this.decrypt(token);
      const payload = JSON.parse(decrypted);
      
      // Check expiration
      if (payload.exp < Math.floor(Date.now() / 1000)) {
        return null;
      }
      
      return {
        username: payload.username,
        exp: payload.exp
      };
    } catch (error) {
      console.error('Token verification failed:', error);
      return null;
    }
  }
}
