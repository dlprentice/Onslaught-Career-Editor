/* address: 0x004dab50 */
/* name: CRound__RemoveActiveReaderById */
/* signature: void __fastcall CRound__RemoveActiveReaderById(void * param_1) */


void __fastcall CRound__RemoveActiveReaderById(void *param_1)

{
  void *this;
  int unaff_EDI;

  this = *(void **)((int)param_1 + 0xec);
  if ((this != (void *)0x0) && ((*(byte *)((int)this + 0x34) & 8) != 0)) {
    CMonitor__RemoveActiveReaderById(this,*(int *)((int)param_1 + 0xe8),unaff_EDI);
  }
  if ((*(int *)((int)param_1 + 0xe8) != 0) &&
     ((*(byte *)(*(int *)((int)param_1 + 0xe8) + 0x34) & 8) != 0)) {
    CSPtrSet__Remove(&DAT_008551a0,param_1);
  }
  CGenericActiveReader__SetReader((void *)((int)param_1 + 0xe8),(void *)0x0);
  return;
}
