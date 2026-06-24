/* address: 0x005d0a2a */
/* name: CFEPSaveGame__Helper_005d0a2a */
/* signature: uint __cdecl CFEPSaveGame__Helper_005d0a2a(uint param_1) */


uint __cdecl CFEPSaveGame__Helper_005d0a2a(uint param_1)

{
  ushort uVar1;
  uint uVar2;
  int iVar3;
  undefined2 uVar4;
  undefined4 in_ECX;

  uVar1 = (ushort)param_1;
  if (uVar1 == 0xffff) {
    return param_1;
  }
  if (DAT_009d0998 == 0) {
    if ((0x40 < uVar1) && (uVar1 < 0x5b)) {
      return param_1 + 0x20;
    }
  }
  else {
    if (uVar1 < 0x100) {
      uVar2 = CRT__GetCharTypeMaskCompat(param_1,1);
      if (uVar2 == 0) {
        return param_1 & 0xffff;
      }
    }
    iVar3 = CRT__LCMapStringW_AnsiCompat();
    uVar4 = (undefined2)((uint)iVar3 >> 0x10);
    param_1 = CONCAT22(uVar4,uVar1);
    if (iVar3 != 0) {
      param_1 = CONCAT22(uVar4,(short)((uint)in_ECX >> 0x10));
    }
  }
  return param_1;
}
