/* address: 0x00572f80 */
/* name: CFastVB__Helper_00572f80 */
/* signature: int __fastcall CFastVB__Helper_00572f80(int param_1) */


int __fastcall CFastVB__Helper_00572f80(int param_1)

{
  if (*(int *)(param_1 + 4) == 0) {
    return 0;
  }
  return *(int *)(param_1 + 0xc) - *(int *)(param_1 + 4) >> 1;
}
