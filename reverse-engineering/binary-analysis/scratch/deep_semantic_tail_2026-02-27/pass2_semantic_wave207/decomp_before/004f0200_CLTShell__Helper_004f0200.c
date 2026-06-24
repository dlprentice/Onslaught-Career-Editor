/* address: 0x004f0200 */
/* name: CLTShell__Helper_004f0200 */
/* signature: void __stdcall CLTShell__Helper_004f0200(int param_1) */


void CLTShell__Helper_004f0200(int param_1)

{
  int *piVar1;
  int aLevel;
  undefined4 *puVar2;
  int iVar3;
  char local_200 [256];
  char local_100 [256];

  DAT_0083d454 = param_1;
  iVar3 = 0;
  DAT_0083d458 = 0;
  if (DAT_00632b04 != -1) {
    puVar2 = &DAT_00632b04;
    do {
      piVar1 = puVar2 + 1;
      puVar2 = puVar2 + 1;
    } while (*piVar1 != -1);
  }
  do {
    do {
      DAT_0083d458 = DAT_0083d458 + 1;
      sprintf(local_100,s______STRESS_TEST_________Iterati_00632c8c);
      DebugTrace(local_100);
      aLevel = (&DAT_00632b04)[iVar3];
      CFrontEnd__Run(&DAT_0089d758,0,0);
      CLTShell__Helper_00549310();
      sprintf(local_200,s_Before_level__d_00632c7c);
      CMemoryManager__DumpMemoryReport(local_200);
      DAT_008a1815 = 1;
      CGame__RunLevel(&DAT_008a9a98,aLevel);
      sprintf(local_200,s_After_level__d_00632c6c);
      CMemoryManager__DumpMemoryReport(local_200);
      CLTShell__Helper_00549310();
      sprintf(local_100,s_Deltas_for_level__d_00632c54);
      DebugTrace(local_100);
      CLTShell__Helper_005492d0(0x9c3df0);
      piVar1 = &DAT_00632b08 + iVar3;
      iVar3 = iVar3 + 1;
    } while (*piVar1 != -1);
    iVar3 = 0;
  } while( true );
}
