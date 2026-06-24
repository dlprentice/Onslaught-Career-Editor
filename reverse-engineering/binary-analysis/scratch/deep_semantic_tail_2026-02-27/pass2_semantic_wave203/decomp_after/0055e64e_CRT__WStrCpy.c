/* address: 0x0055e64e */
/* name: CRT__WStrCpy */
/* signature: void __cdecl CRT__WStrCpy(void * param_1, void * param_2) */


void __cdecl CRT__WStrCpy(void *param_1,void *param_2)

{
  short sVar1;

  sVar1 = *(short *)param_2;
  *(short *)param_1 = sVar1;
  while( true ) {
    param_1 = (void *)((int)param_1 + 2);
    param_2 = (void *)((int)param_2 + 2);
    if (sVar1 == 0) break;
    sVar1 = *(short *)param_2;
    *(short *)param_1 = sVar1;
  }
  return;
}
