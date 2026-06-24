/* address: 0x0056cbe2 */
/* name: CRT__Tzset */
/* signature: void CRT__Tzset(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CRT__Tzset(void)

{
  char cVar1;
  char cVar2;
  char *_Str1;
  DWORD DVar3;
  int iVar4;
  size_t sVar5;
  char *_Source;
  int local_8;

  CDXTexture__Helper_00561179(0xc);
  DAT_00656a30 = 0xffffffff;
  DAT_00656a20 = 0xffffffff;
  DAT_009d0b40 = 0;
  _Str1 = (char *)CTexture__Helper_0056e271(&DAT_005e685c);
  if (_Str1 == (char *)0x0) {
    CTexture__Helper_005611da(0xc);
    DVar3 = GetTimeZoneInformation((LPTIME_ZONE_INFORMATION)&DAT_009d0b48);
    if (DVar3 == 0xffffffff) {
      return;
    }
    DAT_00656988 = DAT_009d0b48 * 0x3c;
    DAT_009d0b40 = 1;
    if (DAT_009d0b8e != 0) {
      DAT_00656988 = DAT_00656988 + DAT_009d0b9c * 0x3c;
    }
    if ((DAT_009d0be2 == 0) || (DAT_009d0bf0 == 0)) {
      DAT_0065698c = 0;
      _DAT_00656990 = 0;
    }
    else {
      DAT_0065698c = 1;
      _DAT_00656990 = (DAT_009d0bf0 - DAT_009d0b9c) * 0x3c;
    }
    iVar4 = WideCharToMultiByte(DAT_009d09a8,0x220,(LPCWSTR)&DAT_009d0b4c,-1,PTR_DAT_00656a14,0x3f,
                                (LPCSTR)0x0,&local_8);
    if ((iVar4 == 0) || (local_8 != 0)) {
      *PTR_DAT_00656a14 = 0;
    }
    else {
      PTR_DAT_00656a14[0x3f] = 0;
    }
    iVar4 = WideCharToMultiByte(DAT_009d09a8,0x220,(LPCWSTR)&DAT_009d0ba0,-1,PTR_DAT_00656a18,0x3f,
                                (LPCSTR)0x0,&local_8);
    if ((iVar4 != 0) && (local_8 == 0)) {
      PTR_DAT_00656a18[0x3f] = 0;
      return;
    }
LAB_0056ce53:
    *PTR_DAT_00656a18 = 0;
  }
  else {
    if ((*_Str1 != '\0') &&
       ((DAT_009d0bf4 == (char *)0x0 || (iVar4 = _strcmp(_Str1,DAT_009d0bf4), iVar4 != 0)))) {
      CMeshCollisionVolume__Unk_0055f085((int)DAT_009d0bf4);
      sVar5 = _strlen(_Str1);
      DAT_009d0bf4 = _malloc(sVar5 + 1);
      if (DAT_009d0bf4 != (char *)0x0) {
        CDXTexture__Helper_00567de0(DAT_009d0bf4,_Str1);
        CTexture__Helper_005611da(0xc);
        _strncpy(PTR_DAT_00656a14,_Str1,3);
        _Source = _Str1 + 3;
        PTR_DAT_00656a14[3] = 0;
        cVar1 = *_Source;
        if (cVar1 == '-') {
          _Source = _Str1 + 4;
        }
        iVar4 = CTexture__Helper_0055e21b(_Source);
        DAT_00656988 = iVar4 * 0xe10;
        for (; (cVar2 = *_Source, cVar2 == '+' || (('/' < cVar2 && (cVar2 < ':'))));
            _Source = _Source + 1) {
        }
        if (*_Source == ':') {
          _Source = _Source + 1;
          iVar4 = CTexture__Helper_0055e21b(_Source);
          DAT_00656988 = DAT_00656988 + iVar4 * 0x3c;
          for (; ('/' < *_Source && (*_Source < ':')); _Source = _Source + 1) {
          }
          if (*_Source == ':') {
            _Source = _Source + 1;
            iVar4 = CTexture__Helper_0055e21b(_Source);
            DAT_00656988 = DAT_00656988 + iVar4;
            for (; ('/' < *_Source && (*_Source < ':')); _Source = _Source + 1) {
            }
          }
        }
        if (cVar1 == '-') {
          DAT_00656988 = -DAT_00656988;
        }
        DAT_0065698c = (int)*_Source;
        if (DAT_0065698c != 0) {
          _strncpy(PTR_DAT_00656a18,_Source,3);
          PTR_DAT_00656a18[3] = 0;
          return;
        }
        goto LAB_0056ce53;
      }
    }
    CTexture__Helper_005611da(0xc);
  }
  return;
}
