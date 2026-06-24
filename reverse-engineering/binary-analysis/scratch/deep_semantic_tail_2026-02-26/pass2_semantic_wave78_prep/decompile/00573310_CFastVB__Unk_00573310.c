/* address: 0x00573310 */
/* name: CFastVB__Unk_00573310 */
/* signature: int __fastcall CFastVB__Unk_00573310(int param_1) */


int __fastcall CFastVB__Unk_00573310(int param_1)

{
  if (*(int *)(param_1 + 4) == 0) {
    return 0;
  }
  return *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 2;
}
