/* address: 0x004b7b60 */
/* name: CDropship__RequestQueueAdvance */
/* signature: void __fastcall CDropship__RequestQueueAdvance(int param_1) */


void __fastcall CDropship__RequestQueueAdvance(int param_1)

{
  *(undefined4 *)(param_1 + 0x2c0) = 1;
  CDropship__TryAdvanceQueuedPortrait((void *)param_1);
  return;
}
