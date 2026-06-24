/* address: 0x00505ab0 */
/* name: CWaypointManager__Unk_00505ab0 */
/* signature: void CWaypointManager__Unk_00505ab0(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CWaypointManager__Unk_00505ab0(void)

{
  undefined4 *value;

  while( true ) {
    DAT_00854fc8 = DAT_00854fc0;
    if ((DAT_00854fc0 == (undefined4 *)0x0) ||
       (value = (undefined4 *)*DAT_00854fc0, value == (undefined4 *)0x0)) break;
    CSPtrSet__Remove(&DAT_00854fc0,value);
    (**(code **)*value)(1);
  }
  return;
}
