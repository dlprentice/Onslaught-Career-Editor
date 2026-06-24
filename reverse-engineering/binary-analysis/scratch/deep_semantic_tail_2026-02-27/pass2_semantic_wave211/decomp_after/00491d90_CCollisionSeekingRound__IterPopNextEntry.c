/* address: 0x00491d90 */
/* name: CCollisionSeekingRound__IterPopNextEntry */
/* signature: int __fastcall CCollisionSeekingRound__IterPopNextEntry(void * param_1) */


int __fastcall CCollisionSeekingRound__IterPopNextEntry(void *param_1)

{
  if (*(undefined4 **)param_1 != (undefined4 *)0x0) {
    *(undefined4 *)param_1 = **(undefined4 **)param_1;
  }
  return *(int *)param_1;
}
