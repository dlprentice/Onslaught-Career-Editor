/* address: 0x005016b0 */
/* name: CEngine__Unk_005016b0 */
/* signature: void CEngine__Unk_005016b0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CEngine__Unk_005016b0(void)

{
  undefined1 local_130 [196];
  uint uStack_6c;

  if (DAT_00888c8c != 0) {
    (**(code **)(*DAT_00888a50 + 0x1c))(DAT_00888a50,local_130);
    DAT_00854e6c = uStack_6c < 0xfffe0101;
  }
  if (DAT_0063c108 != '\0') {
    (**(code **)(*DAT_00665848 + 0x14))(&DAT_00854e10);
    CConsole__RegisterVariable
              (s_cg_forcevertexshaders_0063cde8,s_Should_vertex_shaders_be_used_wh_0063ce00,3,
               &DAT_00854e6d,0,0);
  }
  return;
}
