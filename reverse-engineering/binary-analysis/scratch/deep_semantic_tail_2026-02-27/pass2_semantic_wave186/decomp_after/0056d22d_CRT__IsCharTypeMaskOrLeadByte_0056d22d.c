/* address: 0x0056d22d */
/* name: CRT__IsCharTypeMaskOrLeadByte_0056d22d */
/* signature: int __cdecl CRT__IsCharTypeMaskOrLeadByte_0056d22d(int param_1, uint param_2, int param_3) */


int __cdecl CRT__IsCharTypeMaskOrLeadByte_0056d22d(int param_1,uint param_2,int param_3)

{
  uint uVar1;

  if ((*(byte *)((int)&DAT_009d34c0 + (param_1 & 0xffU) + 1) & (byte)param_3) == 0) {
    if (param_2 == 0) {
      uVar1 = 0;
    }
    else {
      uVar1 = *(ushort *)(&DAT_0065389a + (param_1 & 0xffU) * 2) & param_2;
    }
    if (uVar1 == 0) {
      return 0;
    }
  }
  return 1;
}
