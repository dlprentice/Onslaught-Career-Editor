/* address: 0x00428bc0 */
/* name: CFrontEndPage__Unk_00428bc0 */
/* signature: double __fastcall CFrontEndPage__Unk_00428bc0(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __fastcall CFrontEndPage__Unk_00428bc0(int param_1)

{
  if (*(int *)(param_1 + 0x26c) != 0) {
    return (double)(*(float *)(*(int *)(param_1 + 0x26c) + 0x114) + *(float *)(param_1 + 0x274));
  }
  return (double)_DAT_005d856c;
}
