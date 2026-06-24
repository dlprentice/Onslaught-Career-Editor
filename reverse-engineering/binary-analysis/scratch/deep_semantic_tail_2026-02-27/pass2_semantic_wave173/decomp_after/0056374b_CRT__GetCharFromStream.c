/* address: 0x0056374b */
/* name: CRT__GetCharFromStream */
/* signature: uint __cdecl CRT__GetCharFromStream(void * param_1) */


uint __cdecl CRT__GetCharFromStream(void *param_1)

{
  int *piVar1;
  byte bVar2;
  uint uVar3;

  piVar1 = (int *)((int)param_1 + 4);
  *piVar1 = *piVar1 + -1;
  if (-1 < *piVar1) {
    bVar2 = **(byte **)param_1;
    *(byte **)param_1 = *(byte **)param_1 + 1;
    return (uint)bVar2;
  }
  uVar3 = CRT__ReadByteWithBufferRefill(param_1);
  return uVar3;
}
