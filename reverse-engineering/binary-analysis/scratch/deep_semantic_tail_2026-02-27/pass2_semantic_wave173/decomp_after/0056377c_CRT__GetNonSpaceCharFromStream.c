/* address: 0x0056377c */
/* name: CRT__GetNonSpaceCharFromStream */
/* signature: uint __cdecl CRT__GetNonSpaceCharFromStream(void * param_1, void * param_2) */


uint __cdecl CRT__GetNonSpaceCharFromStream(void *param_1,void *param_2)

{
  void *pvVar1;
  uint uVar2;
  void *this;
  void *pvVar3;

  do {
    *(int *)param_1 = *(int *)param_1 + 1;
    pvVar3 = param_2;
    pvVar1 = (void *)CRT__GetCharFromStream(param_2);
    uVar2 = CRT__IsCharTypeMask0x08(this,pvVar1,(int)pvVar3);
  } while (uVar2 != 0);
  return (uint)pvVar1;
}
