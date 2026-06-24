/* address: 0x0056f280 */
/* name: CFastVB__CountWordElements */
/* signature: int __fastcall CFastVB__CountWordElements(int param_1) */


int __fastcall CFastVB__CountWordElements(int param_1)

{
  if (*(int *)(param_1 + 4) == 0) {
    return 0;
  }
  return *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 1;
}
