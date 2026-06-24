/* address: 0x00501360 */
/* name: CWaypoint__CleanupEndLevelVBufTextures */
/* signature: void CWaypoint__CleanupEndLevelVBufTextures(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWaypoint__CleanupEndLevelVBufTextures(void)

{
  int *piVar1;
  int *obj;
  int *piVar2;
  char local_100 [256];

  piVar1 = DAT_00854e00;
  piVar2 = DAT_00854e00;
  while (obj = piVar1, DAT_00854e00 = piVar2, obj != (int *)0x0) {
    piVar1 = (int *)obj[0x16];
    if ((obj[0x18] == 0) && (obj != (int *)0x0)) {
      CVBufTexture__dtor();
      OID__FreeObject(obj);
      piVar2 = DAT_00854e00;
    }
  }
  if (piVar2 == (int *)0x0) {
    DebugTrace(s_No_end_of_level_VBufTexture_reso_00633e8c);
    return;
  }
  DebugTrace(s__________________________________00633fa4);
  DebugTrace(s_VBufTexture_end_of_level_resourc_00633f78);
  DebugTrace(s__________________________________00633f4c);
  do {
    if (*piVar2 == 0) {
      sprintf(local_100,s_VBufTexture_for_NULL_texture_lea_00633ee4);
    }
    else {
      sprintf(local_100,s_VBufTexture_for_texture___s__lea_00633f18);
    }
    DebugTrace(local_100);
    piVar2 = (int *)piVar2[0x16];
  } while (piVar2 != (int *)0x0);
  DebugTrace(s__________________________________00633eb8);
  return;
}
