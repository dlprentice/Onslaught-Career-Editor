/* address: 0x004a5430 */
/* name: CMesh__FreeUnusedAndReportLeaks */
/* signature: void CMesh__FreeUnusedAndReportLeaks(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CMesh__FreeUnusedAndReportLeaks(void)

{
  void *pvVar1;
  bool bVar2;
  void *pvVar3;
  char local_100 [256];

  DAT_00704ae0 = 0;
  do {
    bVar2 = true;
    pvVar3 = DAT_00704ad8;
    if (DAT_00704ad8 == (void *)0x0) break;
    do {
      pvVar1 = *(void **)((int)pvVar3 + 0x158);
      if ((*(int *)((int)pvVar3 + 0x170) == 0) && (bVar2 = false, pvVar3 != (void *)0x0)) {
        CMesh__FreeResourcesAndUnlink(pvVar3);
        OID__FreeObject(pvVar3);
      }
      pvVar3 = pvVar1;
    } while (pvVar1 != (void *)0x0);
  } while (!bVar2);
  pvVar3 = DAT_00704ad8;
  DebugTrace(s_________________________________0062fa24);
  DebugTrace(s_Mesh_end_of_level_resource_leaks_0062fa00);
  DebugTrace(s_________________________________0062f9dc);
  for (; pvVar3 != (void *)0x0; pvVar3 = *(void **)((int)pvVar3 + 0x158)) {
    sprintf(local_100,s_Mesh___s__leaked___refcount__d_0062f938);
    DebugTrace(local_100);
  }
  DebugTrace(s________________________________0062f9b8);
  return;
}
