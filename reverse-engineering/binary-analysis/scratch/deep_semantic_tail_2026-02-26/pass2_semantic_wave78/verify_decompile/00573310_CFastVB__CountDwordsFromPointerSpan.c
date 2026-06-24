/* address: 0x00573310 */
/* name: CFastVB__CountDwordsFromPointerSpan */
/* signature: int __fastcall CFastVB__CountDwordsFromPointerSpan(int param_1) */


int __fastcall CFastVB__CountDwordsFromPointerSpan(int param_1)

{
  if (*(int *)(param_1 + 4) == 0) {
    return 0;
  }
  return *(int *)(param_1 + 8) - *(int *)(param_1 + 4) >> 2;
}
