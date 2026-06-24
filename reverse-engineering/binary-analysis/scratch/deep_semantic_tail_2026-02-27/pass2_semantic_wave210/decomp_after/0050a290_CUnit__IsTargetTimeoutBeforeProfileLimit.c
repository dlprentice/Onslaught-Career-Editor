/* address: 0x0050a290 */
/* name: CUnit__IsTargetTimeoutBeforeProfileLimit */
/* signature: int __fastcall CUnit__IsTargetTimeoutBeforeProfileLimit(int param_1) */


int __fastcall CUnit__IsTargetTimeoutBeforeProfileLimit(int param_1)

{
  if (((*(int *)(param_1 + 0xa0) != 0) && (*(int *)(param_1 + 0x6c) != 0)) &&
     (*(int *)(param_1 + 0x6c) < *(int *)(*(int *)(param_1 + 0xa0) + 0x44))) {
    return 1;
  }
  return 0;
}
