/* address: 0x00569449 */
/* name: CRT__ControlFp */
/* signature: uint __cdecl CRT__ControlFp(uint param_1, uint param_2) */


uint __cdecl CRT__ControlFp(uint param_1,uint param_2)

{
  uint uVar1;
  undefined4 in_ECX;
  undefined2 in_FPUControlWord;
  undefined4 local_8;

  local_8 = CONCAT22((short)((uint)in_ECX >> 0x10),in_FPUControlWord);
  uVar1 = CDXTexture__Unk_00569494(local_8);
  uVar1 = uVar1 & ~param_2 | param_1 & param_2;
  CDXTexture__Unk_00569526(uVar1);
  return uVar1;
}
