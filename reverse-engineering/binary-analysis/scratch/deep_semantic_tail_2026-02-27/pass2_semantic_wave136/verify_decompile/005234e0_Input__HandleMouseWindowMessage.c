/* address: 0x005234e0 */
/* name: Input__HandleMouseWindowMessage */
/* signature: int __stdcall Input__HandleMouseWindowMessage(int param_1, uint param_2, uint param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int Input__HandleMouseWindowMessage(int param_1,uint param_2,uint param_3)

{
  float fVar1;
  char cVar2;
  int iVar3;
  short sVar4;

  if (g_bDevModeEnabled != 0) {
    return 0;
  }
  switch(param_1) {
  case 0x200:
    if ((param_2 & 1) == 0) {
      DAT_0089bdf5 = 0;
    }
    if ((param_2 & 2) == 0) {
      DAT_0089bdf7 = 0;
    }
    if ((param_2 & 0x10) == 0) {
      DAT_0089bdf6 = 0;
    }
    if (DAT_0089bdf0 == 0) {
      DAT_0089bda8 = param_3 & 0xffff;
      fVar1 = (float)DAT_0089bda8;
      DAT_0089bda4 = param_3 >> 0x10;
      iVar3 = PLATFORM__GetWindowWidth();
      _DAT_0089bda0 = fVar1 / (float)iVar3;
      fVar1 = (float)(int)DAT_0089bda4;
      iVar3 = PLATFORM__GetWindowHeight();
      _DAT_0089bd9c = fVar1 / (float)iVar3;
    }
    iVar3 = CVBufTexture__Helper_00465f00();
    if ((char)iVar3 != '\0') {
      DAT_0089bda8 = DAT_0089bda8 * 0x280;
      iVar3 = PLATFORM__GetWindowWidth();
      DAT_0089bda8 = (int)DAT_0089bda8 / iVar3;
      DAT_0089bda4 = DAT_0089bda4 * 0x1e0;
      iVar3 = PLATFORM__GetWindowHeight();
      DAT_0089bda4 = (int)DAT_0089bda4 / iVar3;
    }
    _DAT_0089be44 = DAT_0089bda4;
    DAT_0089bdf4 = 1;
    _DAT_0089be40 = DAT_0089bda8;
    return 0;
  case 0x201:
    DAT_0083d3f0 = 1;
    if (((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(0,4), cVar2 == '\0')) &&
       (DAT_0089bdf5 = 1, DAT_0089bdf8 == 0)) {
      DAT_0089bdf8 = 1;
      DAT_0089be00 = param_3 & 0xffff;
      fVar1 = (float)DAT_0089be00;
      DAT_0089be04 = param_3 >> 0x10;
      iVar3 = PLATFORM__GetWindowWidth();
      _DAT_0089be08 = fVar1 / (float)iVar3;
      fVar1 = (float)(int)DAT_0089be04;
      iVar3 = PLATFORM__GetWindowHeight();
      _DAT_0089be0c = fVar1 / (float)iVar3;
      iVar3 = CVBufTexture__Helper_00465f00();
      if ((char)iVar3 != '\0') {
        DAT_0089be00 = DAT_0089be00 * 0x280;
        iVar3 = PLATFORM__GetWindowWidth();
        DAT_0089be00 = (int)DAT_0089be00 / iVar3;
        DAT_0089be04 = DAT_0089be04 * 0x1e0;
        iVar3 = PLATFORM__GetWindowHeight();
        DAT_0089be04 = (int)DAT_0089be04 / iVar3;
        return 0;
      }
    }
    break;
  case 0x202:
    if ((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(0,3), cVar2 == '\0')) {
      DAT_0089bdf5 = 0;
      DAT_0089bdfc = 1;
      return 0;
    }
    break;
  case 0x204:
    DAT_0083d3f0 = 1;
    if (((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(2,4), cVar2 == '\0')) &&
       (DAT_0089bdf7 = 1, DAT_0089be28 == 0)) {
      DAT_0089be28 = 1;
      DAT_0089be30 = param_3 & 0xffff;
      fVar1 = (float)DAT_0089be30;
      DAT_0089be34 = param_3 >> 0x10;
      iVar3 = PLATFORM__GetWindowWidth();
      _DAT_0089be38 = fVar1 / (float)iVar3;
      fVar1 = (float)(int)DAT_0089be34;
      iVar3 = PLATFORM__GetWindowHeight();
      _DAT_0089be3c = fVar1 / (float)iVar3;
      iVar3 = CVBufTexture__Helper_00465f00();
      if ((char)iVar3 != '\0') {
        DAT_0089be30 = DAT_0089be30 * 0x280;
        iVar3 = PLATFORM__GetWindowWidth();
        DAT_0089be30 = (int)DAT_0089be30 / iVar3;
        DAT_0089be34 = DAT_0089be34 * 0x1e0;
        iVar3 = PLATFORM__GetWindowHeight();
        DAT_0089be34 = (int)DAT_0089be34 / iVar3;
        return 0;
      }
    }
    break;
  case 0x205:
    if ((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(2,3), cVar2 == '\0')) {
      DAT_0089bdf7 = 0;
      DAT_0089be2c = 1;
      return 0;
    }
    break;
  case 0x207:
    DAT_0083d3f0 = 1;
    if (((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(1,4), cVar2 == '\0')) &&
       (DAT_0089bdf6 = 1, DAT_0089be10 == 0)) {
      DAT_0089be10 = 1;
      DAT_0089be18 = param_3 & 0xffff;
      fVar1 = (float)DAT_0089be18;
      DAT_0089be1c = param_3 >> 0x10;
      iVar3 = PLATFORM__GetWindowWidth();
      _DAT_0089be20 = fVar1 / (float)iVar3;
      fVar1 = (float)(int)DAT_0089be1c;
      iVar3 = PLATFORM__GetWindowHeight();
      _DAT_0089be24 = fVar1 / (float)iVar3;
      iVar3 = CVBufTexture__Helper_00465f00();
      if ((char)iVar3 != '\0') {
        DAT_0089be18 = DAT_0089be18 * 0x280;
        iVar3 = PLATFORM__GetWindowWidth();
        DAT_0089be18 = (int)DAT_0089be18 / iVar3;
        DAT_0089be1c = DAT_0089be1c * 0x1e0;
        iVar3 = PLATFORM__GetWindowHeight();
        DAT_0089be1c = (int)DAT_0089be1c / iVar3;
        return 0;
      }
    }
    break;
  case 0x208:
    if ((DAT_00889008 == (code *)0x0) || (cVar2 = (*DAT_00889008)(1,3), cVar2 == '\0')) {
      DAT_0089be14 = 1;
      DAT_0089bdf6 = 0;
      return 0;
    }
    break;
  case 0x20a:
    sVar4 = (short)(param_2 >> 0x10);
    if (DAT_00889008 != (code *)0x0) {
      if (sVar4 == 0 || (int)param_2 < 0) {
        cVar2 = (*DAT_00889008)(4,3);
      }
      else {
        cVar2 = (*DAT_00889008)(3,3);
      }
      if (cVar2 != '\0') {
        return 0;
      }
    }
    DAT_0089be48 = DAT_0089be48 + sVar4;
  }
  return 0;
}
