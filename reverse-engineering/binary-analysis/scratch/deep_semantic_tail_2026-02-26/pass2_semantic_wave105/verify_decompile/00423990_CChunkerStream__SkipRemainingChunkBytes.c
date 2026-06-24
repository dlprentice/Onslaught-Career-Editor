/* address: 0x00423990 */
/* name: CChunkerStream__SkipRemainingChunkBytes */
/* signature: void __fastcall CChunkerStream__SkipRemainingChunkBytes(void * param_1) */


void __fastcall CChunkerStream__SkipRemainingChunkBytes(void *param_1)

{
  int iVar1;

  iVar1 = *(int *)((int)param_1 + 8);
  *(int *)((int)param_1 + 8) = *(int *)param_1;
  DXMemBuffer__Skip(*(int *)param_1 - iVar1);
  return;
}
