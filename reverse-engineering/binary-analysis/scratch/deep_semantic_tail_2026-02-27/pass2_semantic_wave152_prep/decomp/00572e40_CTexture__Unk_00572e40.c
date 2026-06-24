/* address: 0x00572e40 */
/* name: CTexture__Unk_00572e40 */
/* signature: void __fastcall CTexture__Unk_00572e40(int param_1) */


void __fastcall CTexture__Unk_00572e40(int param_1)

{
  int *piVar1;
  int *piVar2;
  void *ptr;
  void *unaff_EBX;
  void *unaff_EDI;
  int *local_c;
  undefined1 local_8 [4];
  undefined1 local_4 [4];

  piVar1 = *(int **)(param_1 + 4);
  local_c = (int *)*piVar1;
  piVar2 = local_c;
  if (*(int *)(param_1 + 0xc) == 0) {
    while (local_c = piVar2, piVar2 != piVar1) {
      CTexture__Unk_00574180(&local_c);
      CTexture__Unk_005738e0((void *)param_1,(int)local_4,piVar2,unaff_EBX);
      piVar2 = local_c;
    }
  }
  else {
    CTexture__Unk_00573cc0((void *)piVar1[1]);
    *(void **)(*(int *)(param_1 + 4) + 4) = DAT_009d0c44;
    *(undefined4 *)(param_1 + 0xc) = 0;
    *(undefined4 *)*(undefined4 *)(param_1 + 4) = *(undefined4 *)(param_1 + 4);
    *(int *)(*(int *)(param_1 + 4) + 8) = *(int *)(param_1 + 4);
    CTexture__Helper_00573330((void *)param_1,(int)local_8,unaff_EDI);
  }
  OID__FreeObject_Callback(*(void **)(param_1 + 4));
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)(param_1 + 0xc) = 0;
  ptr = DAT_009d0c44;
  DAT_009d0c48 = DAT_009d0c48 + -1;
  if ((DAT_009d0c48 == 0) && (DAT_009d0c44 = (void *)0x0, ptr != (void *)0x0)) {
    OID__FreeObject_Callback(ptr);
  }
  return;
}
