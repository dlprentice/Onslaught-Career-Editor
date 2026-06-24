/* address: 0x00573d00 */
/* name: RBTree__InitUIntKeyTreeWithSharedSentinel */
/* signature: void __fastcall RBTree__InitUIntKeyTreeWithSharedSentinel(int param_1) */


void __fastcall RBTree__InitUIntKeyTreeWithSharedSentinel(int param_1)

{
  undefined4 *extraout_EAX;
  int extraout_EAX_00;
  undefined4 *puVar1;

  CFastVB__Helper_00426fd0(0x14);
  extraout_EAX[4] = 1;
  extraout_EAX[1] = 0;
  puVar1 = extraout_EAX;
  if (DAT_009d0c44 == (undefined4 *)0x0) {
    DAT_009d0c44 = extraout_EAX;
    *extraout_EAX = 0;
    puVar1 = (undefined4 *)0x0;
    DAT_009d0c44[2] = 0;
  }
  DAT_009d0c48 = DAT_009d0c48 + 1;
  if (puVar1 != (undefined4 *)0x0) {
    OID__FreeObject_Callback(puVar1);
  }
  puVar1 = DAT_009d0c44;
  CFastVB__Helper_00426fd0(0x14);
  *(undefined4 **)(extraout_EAX_00 + 4) = puVar1;
  *(undefined4 *)(extraout_EAX_00 + 0x10) = 0;
  *(int *)(param_1 + 4) = extraout_EAX_00;
  *(undefined4 *)(param_1 + 0xc) = 0;
  *(int *)extraout_EAX_00 = extraout_EAX_00;
  *(int *)(*(int *)(param_1 + 4) + 8) = *(int *)(param_1 + 4);
  return;
}
