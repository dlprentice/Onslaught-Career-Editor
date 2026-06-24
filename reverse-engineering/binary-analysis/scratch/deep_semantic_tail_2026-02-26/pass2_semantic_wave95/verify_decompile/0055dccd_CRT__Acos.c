/* address: 0x0055dccd */
/* name: CRT__Acos */
/* signature: double __cdecl CRT__Acos(int param_1, uint param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __cdecl CRT__Acos(int param_1,uint param_2)

{
  uint in_EAX;
  uint extraout_EAX;
  bool in_ZF;
  short in_FPUControlWord;
  float10 in_ST0;
  float10 extraout_ST0;
  float10 extraout_ST0_00;
  float10 fVar1;

  if (in_ZF) {
    if (((in_EAX & 0xfffff) != 0) || (fVar1 = _DAT_00653730, param_1 != 0)) {
      CDXTexture__Unk_005615bc();
      fVar1 = extraout_ST0_00;
    }
LAB_0055dd5c:
    if (DAT_009d08b4 == 0) {
      fVar1 = (float10)__startOneArgErrorHandling();
      return (double)fVar1;
    }
  }
  else {
    if (in_FPUControlWord != 0x27f) {
      CDXTexture__Unk_005615a5();
      in_EAX = extraout_EAX;
      in_ST0 = extraout_ST0;
    }
    if (in_EAX < 0x3ff00000) {
      fVar1 = (float10)fpatan(in_ST0,SQRT(((float10)1 - in_ST0) * ((float10)1 + in_ST0)));
    }
    else {
      fVar1 = _DAT_00653730;
      if ((0x3ff00000 < in_EAX) || ((param_2 & 0xfffff) != 0 || param_1 != 0)) goto LAB_0055dd5c;
      fVar1 = _DAT_0065373a;
      if ((param_2 & 0x80000000) != 0) {
        fVar1 = -_DAT_0065373a;
      }
    }
    if (DAT_009d08b4 == 0) {
      fVar1 = (float10)__math_exit();
      return (double)fVar1;
    }
  }
  return (double)fVar1;
}
