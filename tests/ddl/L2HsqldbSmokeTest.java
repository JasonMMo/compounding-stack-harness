/**
 * L2HsqldbSmokeTest.java -- L2 fulltest gate (Growth-10).
 * QA-authored. HSQLDB 2.x in-memory JDBC. No external framework.
 * Usage: python tests/ddl/run_l2.py
 */
import java.io.*;
import java.nio.file.*;
import java.sql.*;
import java.util.*;

public class L2HsqldbSmokeTest {
    static int passed=0, failed=0;
    static final List<String> failures=new ArrayList<>();
    static final List<String> defects=new ArrayList<>();

    static void pass(String id,String d){
        System.out.println("  PASS  ["+id+"] "+d);passed++;}
    static void fail(String id,String d,String x){
        System.out.println("  FAIL  ["+id+"] "+d+" -- "+x);
        failures.add(id+": "+d+" -- "+x);failed++;}
    static void defect(String id,String d,String x){
        System.out.println("  DEFECT["+id+"] "+d+" -- "+x);
        defects.add(id+": "+d+" -- "+x);failed++;}

    static void assertOk(Connection c,String id,String d,String sql){
        try(Statement st=c.createStatement()){st.executeUpdate(sql);pass(id,d);}
        catch(SQLException e){fail(id,d,"Unexpected: ["+e.getSQLState()+"] "+e.getMessage());}}

    static void assertViolation(Connection c,String id,String d,String sql){
        try(Statement st=c.createStatement()){st.executeUpdate(sql);
            fail(id,d,"Expected violation but succeeded");}
        catch(SQLException e){pass(id,d+" (caught:"+e.getSQLState()+")");}}

    static void assertRowCount(Connection c,String id,String d,String sql,int exp){
        try(Statement st=c.createStatement();ResultSet rs=st.executeQuery(sql)){
            int n=0;while(rs.next())n++;
            if(n==exp)pass(id,d+" (rows="+n+")");else fail(id,d,"Expected "+exp+" rows, got "+n);}
        catch(SQLException e){fail(id,d,e.getMessage());}}

    static void assertColNull(Connection c,String id,String d,String sql,String col){
        try(Statement st=c.createStatement();ResultSet rs=st.executeQuery(sql)){
            if(!rs.next()){fail(id,d,"No rows");return;}
            Object vv=rs.getObject(col);
            if(vv==null)pass(id,d+" (NULL as expected)");else fail(id,d,"Expected NULL for "+col+" got: "+vv);}
        catch(SQLException e){fail(id,d,e.getMessage());}}

    static boolean loadSchema(Connection conn,Path p) throws IOException {
        String sql=Files.readString(p);
        String[] stmts=sql.split(";");
        int ok=0,err=0;List<String> errs=new ArrayList<>();
        for(String raw:stmts){
            String s=raw.strip();
            // Strip leading comment lines
            String[] slines = s.split("\n");
            StringBuilder sb = new StringBuilder();
            for(String sl : slines){
                String sltr = sl.strip();
                if(!sltr.startsWith("--")) sb.append(sl).append("\n");
            }
            s = sb.toString().strip();
            if(s.isEmpty())continue;
            try(Statement st=conn.createStatement()){st.execute(s);ok++;}
            catch(SQLException e){err++;errs.add("["+e.getSQLState()+"] "+e.getMessage());
                if(errs.size()<=5){System.out.println("    ERR: "+e.getMessage().substring(0,Math.min(120,e.getMessage().length())));
                System.out.println("    SQL: "+s.substring(0,Math.min(80,s.length())));}}
        }
        System.out.println("  Schema load: "+ok+" OK, "+err+" errors");
        if(err>0){
            boolean fwd=errs.stream().anyMatch(e->e.toLowerCase().contains("not found")||e.toLowerCase().contains("hr_employee"));
            if(fwd)defect("S0",
                "Forward-FK: hr_department.manager_id emitted before hr_employee",
                "render.py topological sort places hr_department before hr_employee (circular cycle). "
                +"HSQLDB rejects FK to non-existent table at CREATE TABLE time. "
                +"Fix: detect circular back-edge and defer via ALTER TABLE ADD CONSTRAINT.");
            else defect("S0","Schema load failed ("+err+" errors)",errs.get(0));
            return false;}
        pass("S0","Schema load: all "+ok+" DDL statements OK");
        return true;}

    static boolean loadSchemaPatched(Connection conn,Path p) throws IOException {
        // This loads a schema that was pre-patched by the Python patch script.
        // Patches applied: (1) forward-FK deferred, (2) CHECK col quoting, (3) DEFAULT order.
        String sql=Files.readString(p);
        String[] stmts=sql.split(";");
        int ok=0,err=0;List<String> errs=new ArrayList<>();
        for(String raw:stmts){
            String[] slines = raw.split("\n");
            StringBuilder sb = new StringBuilder();
            for(String sl : slines){
                String sltr = sl.strip();
                if(!sltr.startsWith("--")) sb.append(sl).append("\n");
            }
            String s = sb.toString().strip();
            if(s.isEmpty())continue;
            try(Statement st=conn.createStatement()){st.execute(s);ok++;}
            catch(SQLException e){err++;errs.add("["+e.getSQLState()+"] "+e.getMessage());
                System.out.println("    PATCH_ERR: "+e.getMessage().substring(0,Math.min(120,e.getMessage().length())));}}
        System.out.println("  Patched load: "+ok+" OK, "+err+" errors");
        if(err>0){defect("S0-patch","Patched load failed "+err+" errors",errs.get(0));return false;}
        return true;}

    static void runPositiveInserts(Connection conn){
        System.out.println("\n--- S1: Positive inserts ---");
        assertOk(conn,"S1-01","document_category","INSERT INTO \"document_category\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\") VALUES ('dc-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','HR-DOCS','HR Documents')");
        assertOk(conn,"S1-02","hr_department","INSERT INTO \"hr_department\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\") VALUES ('dept-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ENG','Engineering')");
        assertOk(conn,"S1-03","hr_position","INSERT INTO \"hr_position\" (\"id\",\"created_at\",\"updated_at\",\"title\",\"department_id\") VALUES ('pos-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','Software Engineer','dept-001')");
        assertOk(conn,"S1-04","hr_employee (active)","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"full_name\",\"department_id\",\"position_id\",\"hire_date\",\"status\") VALUES ('emp-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP001','Alice Smith','dept-001','pos-001',DATE '2025-01-01','active')");
        assertOk(conn,"S1-05","hr_leave_request (end>=start)","INSERT INTO \"hr_leave_request\" (\"id\",\"created_at\",\"updated_at\",\"employee_id\",\"leave_type\",\"start_date\",\"end_date\",\"status\") VALUES ('lr-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','emp-001','annual',DATE '2026-03-01',DATE '2026-03-05','draft')");
        assertOk(conn,"S1-06","finance_account","INSERT INTO \"finance_account\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"type\",\"currency\",\"is_active\") VALUES ('acct-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','1000','Cash','asset','USD',TRUE)");
        assertOk(conn,"S1-07","finance_invoice","INSERT INTO \"finance_invoice\" (\"id\",\"created_at\",\"updated_at\",\"invoice_number\",\"counterparty_id\",\"issue_date\",\"due_date\",\"total_amount\",\"currency\",\"status\") VALUES ('inv-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','INV-001','cp-001',DATE '2026-01-01',DATE '2026-01-31',1000.0000,'USD','draft')");
        assertOk(conn,"S1-08","finance_payment (500>0)","INSERT INTO \"finance_payment\" (\"id\",\"created_at\",\"updated_at\",\"invoice_id\",\"payment_date\",\"amount\",\"method\") VALUES ('pay-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','inv-001',DATE '2026-01-15',500.0000,'bank-transfer')");
        assertOk(conn,"S1-09","logistics_carrier","INSERT INTO \"logistics_carrier\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"is_active\") VALUES ('car-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','DHL','DHL Express',TRUE)");
        assertOk(conn,"S1-10","logistics_route (transit=3>0)","INSERT INTO \"logistics_route\" (\"id\",\"created_at\",\"updated_at\",\"name\",\"carrier_id\",\"origin_hub\",\"destination_hub\",\"transit_days\",\"is_active\") VALUES ('rte-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','Seoul-Busan','car-001','SEL','PUS',3,TRUE)");
        assertOk(conn,"S1-11","logistics_shipment","INSERT INTO \"logistics_shipment\" (\"id\",\"created_at\",\"updated_at\",\"shipment_number\",\"carrier_id\",\"route_id\",\"origin_address\",\"destination_address\",\"status\") VALUES ('shp-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','SHP-001','car-001','rte-001','Seoul HQ','Busan WH','draft')");
        assertOk(conn,"S1-12","logistics_tracking_event","INSERT INTO \"logistics_tracking_event\" (\"id\",\"created_at\",\"updated_at\",\"shipment_id\",\"event_time\",\"event_code\") VALUES ('evt-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','shp-001',TIMESTAMP '2026-01-15 09:00:00','PICKUP')");
        assertOk(conn,"S1-13","inventory_item","INSERT INTO \"inventory_item\" (\"id\",\"created_at\",\"updated_at\",\"sku\",\"name\",\"unit_of_measure\",\"allow_negative_stock\") VALUES ('itm-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','SKU-001','Widget A','pcs',FALSE)");
        assertOk(conn,"S1-14","inventory_warehouse","INSERT INTO \"inventory_warehouse\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"is_active\") VALUES ('wh-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','WH-MAIN','Main Warehouse',TRUE)");
        assertOk(conn,"S1-15","inventory_stock_level (composite)","INSERT INTO \"inventory_stock_level\" (\"id\",\"created_at\",\"updated_at\",\"item_id\",\"warehouse_id\",\"quantity_on_hand\",\"quantity_reserved\",\"quantity_available\") VALUES ('sl-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','itm-001','wh-001',100.0000,10.0000,90.0000)");
        assertOk(conn,"S1-16","crm_contact","INSERT INTO \"crm_contact\" (\"id\",\"created_at\",\"updated_at\",\"full_name\",\"email\",\"contact_type\") VALUES ('con-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','Bob Jones','bob@example.com','customer')");
        assertOk(conn,"S1-17","crm_opportunity (prob=70)","INSERT INTO \"crm_opportunity\" (\"id\",\"created_at\",\"updated_at\",\"contact_id\",\"name\",\"stage\",\"amount\",\"probability\",\"expected_close_date\",\"owner_id\") VALUES ('opp-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','con-001','Big Deal','qualification',50000.0000,70,DATE '2026-06-30','emp-001')");
        assertOk(conn,"S1-18","sales_price_list","INSERT INTO \"sales_price_list\" (\"id\",\"created_at\",\"updated_at\",\"name\",\"currency\",\"valid_from\",\"is_default\") VALUES ('pl-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','Standard 2026','USD',DATE '2026-01-01',TRUE)");
        assertOk(conn,"S1-19","sales_discount","INSERT INTO \"sales_discount\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"discount_type\",\"value\",\"valid_from\") VALUES ('dis-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','SAVE10','percentage',10.0000,DATE '2026-01-01')");
        assertOk(conn,"S1-20","sales_sales_order","INSERT INTO \"sales_sales_order\" (\"id\",\"created_at\",\"updated_at\",\"order_number\",\"customer_id\",\"order_date\",\"status\",\"currency\",\"total_amount\",\"price_list_id\") VALUES ('ord-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ORD-001','con-001',DATE '2026-01-10','draft','USD',200.0000,'pl-001')");
        assertOk(conn,"S1-21","sales_order_line (qty=2)","INSERT INTO \"sales_sales_order_line\" (\"id\",\"created_at\",\"updated_at\",\"order_id\",\"item_id\",\"quantity\",\"unit_price\",\"line_total\") VALUES ('ol-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ord-001','itm-001',2.0000,100.0000,200.0000)");
        assertOk(conn,"S1-22","project_project (end>=start)","INSERT INTO \"project_project\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"owner_id\",\"status\",\"start_date\",\"end_date\") VALUES ('prj-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','PRJ-001','Alpha','emp-001','active',DATE '2026-01-01',DATE '2026-12-31')");
        assertOk(conn,"S1-23","project_task (pct=50)","INSERT INTO \"project_task\" (\"id\",\"created_at\",\"updated_at\",\"project_id\",\"name\",\"status\",\"progress_pct\") VALUES ('tsk-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','prj-001','Design DB','in-progress',50)");
        assertOk(conn,"S1-24","asset_category (life=5)","INSERT INTO \"asset_category\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"default_useful_life_years\",\"depreciation_method\") VALUES ('acat-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','IT-EQ','IT Equipment',5,'straight-line')");
        assertOk(conn,"S1-25","asset_asset (costs>=0)","INSERT INTO \"asset_asset\" (\"id\",\"created_at\",\"updated_at\",\"asset_number\",\"name\",\"category_id\",\"acquisition_date\",\"acquisition_cost\",\"current_book_value\",\"status\") VALUES ('ast-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','AST-001','Dell Server','acat-001',DATE '2024-01-01',5000.0000,4000.0000,'active')");
        assertOk(conn,"S1-26","procurement_vendor","INSERT INTO \"procurement_vendor\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"is_approved\") VALUES ('vnd-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ACME','ACME Supplies',TRUE)");
        assertOk(conn,"S1-27","quality_inspection_plan","INSERT INTO \"quality_inspection_plan\" (\"id\",\"created_at\",\"updated_at\",\"name\",\"reference_type\",\"reference_id\",\"status\",\"assigned_to\") VALUES ('qip-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','Incoming Check','shipment','shp-001','pending','emp-001')");
        assertOk(conn,"S1-28","approval_request","INSERT INTO \"approval_request\" (\"id\",\"created_at\",\"updated_at\",\"subject_type\",\"subject_id\",\"requester_id\",\"status\",\"title\") VALUES ('apr-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','leave_request','lr-001','emp-001','pending','Leave Approval')");
        assertOk(conn,"S1-29","report_definition","INSERT INTO \"reporting_report_definition\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\",\"domain\",\"output_format\",\"is_active\",\"owner_id\") VALUES ('rpt-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP-RPT','Employee Status','hr','table',TRUE,'emp-001')");
        assertOk(conn,"S1-30","document_document","INSERT INTO \"document_document\" (\"id\",\"created_at\",\"updated_at\",\"title\",\"category_id\",\"owner_id\",\"status\") VALUES ('doc-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','HR Policy','dc-001','emp-001','draft')");
    }

    static void runViolationTests(Connection conn){
        System.out.println("\n--- V: Intended violation tests ---");
        assertViolation(conn,"V1","PK duplicate emp-001","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"full_name\",\"department_id\",\"hire_date\",\"status\") VALUES ('emp-001',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP999','Dup','dept-001',DATE '2025-01-01','active')");
        assertViolation(conn,"V2","UNIQUE employee_number=EMP001","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"full_name\",\"department_id\",\"hire_date\",\"status\") VALUES ('emp-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP001','Clone','dept-001',DATE '2025-01-01','active')");
        assertViolation(conn,"V3","UNIQUE dept.code=ENG","INSERT INTO \"hr_department\" (\"id\",\"created_at\",\"updated_at\",\"code\",\"name\") VALUES ('dept-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ENG','Engineering Clone')");
        assertViolation(conn,"V4","FK restrict dept missing","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"full_name\",\"department_id\",\"hire_date\",\"status\") VALUES ('emp-003',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP003','Ghost','dept-NOEXIST',DATE '2025-01-01','active')");
        assertViolation(conn,"V5","Enum CHECK status=employed","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"full_name\",\"department_id\",\"hire_date\",\"status\") VALUES ('emp-004',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP004','BadStatus','dept-001',DATE '2025-01-01','employed')");
        assertViolation(conn,"V6","CHECK end_date>=start_date reversed","INSERT INTO \"hr_leave_request\" (\"id\",\"created_at\",\"updated_at\",\"employee_id\",\"leave_type\",\"start_date\",\"end_date\",\"status\") VALUES ('lr-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','emp-001','sick',DATE '2026-03-10',DATE '2026-03-01','draft')");
        assertViolation(conn,"V7","CHECK amount>0: payment=0","INSERT INTO \"finance_payment\" (\"id\",\"created_at\",\"updated_at\",\"invoice_id\",\"payment_date\",\"amount\",\"method\") VALUES ('pay-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','inv-001',DATE '2026-01-20',0.0000,'cash')");
        assertViolation(conn,"V8","CHECK prob 0-100: =101","INSERT INTO \"crm_opportunity\" (\"id\",\"created_at\",\"updated_at\",\"contact_id\",\"name\",\"stage\",\"amount\",\"probability\",\"expected_close_date\",\"owner_id\") VALUES ('opp-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','con-001','Bad','qualification',0.0000,101,DATE '2026-06-30','emp-001')");
        assertViolation(conn,"V9","NOT NULL: employee.full_name missing","INSERT INTO \"hr_employee\" (\"id\",\"created_at\",\"updated_at\",\"employee_number\",\"department_id\",\"hire_date\",\"status\") VALUES ('emp-005',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','EMP005','dept-001',DATE '2025-01-01','active')");
        assertViolation(conn,"V10","CHECK qty>0: order_line qty=0","INSERT INTO \"sales_sales_order_line\" (\"id\",\"created_at\",\"updated_at\",\"order_id\",\"item_id\",\"quantity\",\"unit_price\",\"line_total\") VALUES ('ol-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ord-001','itm-001',0.0000,100.0000,0.0000)");
        assertViolation(conn,"V11","Composite UNIQUE (item,wh) dup","INSERT INTO \"inventory_stock_level\" (\"id\",\"created_at\",\"updated_at\",\"item_id\",\"warehouse_id\",\"quantity_on_hand\",\"quantity_reserved\",\"quantity_available\") VALUES ('sl-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','itm-001','wh-001',50.0000,5.0000,45.0000)");
    }

    static void runOnDeleteTests(Connection conn){
        System.out.println("\n--- OD: on_delete behavior tests ---");
        // OD1: ON DELETE SET NULL
        try(Statement st=conn.createStatement()){
            st.executeUpdate("DELETE FROM \"hr_position\" WHERE \"id\" = 'pos-001'");
            pass("OD1-del","DELETE hr_position pos-001");}
        catch(SQLException e){fail("OD1-del","DELETE failed",e.getMessage());return;}
        assertColNull(conn,"OD1-null","ON DELETE SET NULL: emp.position_id=NULL",
            "SELECT \"position_id\" FROM \"hr_employee\" WHERE \"id\" = 'emp-001'","position_id");
        // OD2: ON DELETE RESTRICT
        assertViolation(conn,"OD2","ON DELETE RESTRICT: delete dept with live emp",
            "DELETE FROM \"hr_department\" WHERE \"id\" = 'dept-001'");
        // OD3: ON DELETE CASCADE
        try(Statement st=conn.createStatement()){
            st.executeUpdate("INSERT INTO \"sales_sales_order\" (\"id\",\"created_at\",\"updated_at\",\"order_number\",\"customer_id\",\"order_date\",\"status\",\"currency\",\"total_amount\") VALUES ('ord-002',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ORD-002','con-001',DATE '2026-01-11','draft','USD',50.0000)");
            st.executeUpdate("INSERT INTO \"sales_sales_order_line\" (\"id\",\"created_at\",\"updated_at\",\"order_id\",\"item_id\",\"quantity\",\"unit_price\",\"line_total\") VALUES ('ol-003',TIMESTAMP '2026-01-15 09:00:00',TIMESTAMP '2026-01-15 09:00:00','ord-002','itm-001',1.0000,50.0000,50.0000)");}
        catch(SQLException e){fail("OD3-setup","OD3 setup failed",e.getMessage());return;}
        assertRowCount(conn,"OD3-pre","OD3 pre: line exists","SELECT 1 FROM \"sales_sales_order_line\" WHERE \"order_id\" = 'ord-002'",1);
        try(Statement st=conn.createStatement()){
            st.executeUpdate("DELETE FROM \"sales_sales_order\" WHERE \"id\" = 'ord-002'");
            pass("OD3-del","DELETE sales_order ord-002");}
        catch(SQLException e){fail("OD3-del","DELETE failed",e.getMessage());return;}
        assertRowCount(conn,"OD3-cas","ON DELETE CASCADE: order_line auto-deleted","SELECT 1 FROM \"sales_sales_order_line\" WHERE \"order_id\" = 'ord-002'",0);
    }

    public static void main(String[] args) throws Exception {
        String schemaArg=(args.length>0)?args[0]:"presets/ddl/build/hsqldb-schema.sql";
        Path schema=Path.of(schemaArg);
        if(!Files.exists(schema)){System.err.println("Schema not found: "+schema.toAbsolutePath());System.exit(2);}
        System.out.println("=== L2 HSQLDB Smoke Test -- compounding-stack-harness (Growth-10) ===");
        System.out.println("Schema : "+schema.toAbsolutePath());
        try{System.out.println("HSQLDB : "+org.hsqldb.jdbc.JDBCDriver.class.getPackage().getImplementationVersion());}
        catch(Exception ignore){}
        System.out.println();
        Class.forName("org.hsqldb.jdbc.JDBCDriver");
        System.out.println("--- S0: Schema load ---");
        Connection conn=DriverManager.getConnection("jdbc:hsqldb:mem:l2raw;sql.enforce_strict_size=true","SA","");
        boolean loaded=loadSchema(conn,schema);
        boolean patched=false;
        if(!loaded){
            System.out.println("  Attempting patched load...");
            conn.close();
            conn=DriverManager.getConnection("jdbc:hsqldb:mem:l2patch;sql.enforce_strict_size=true","SA","");
            // Try loading *-patched.sql if it exists (pre-patched by Python script)
            Path patchedSchema = schema.getParent().resolve(schema.getFileName().toString().replace(".sql","-patched.sql"));
            if(!java.nio.file.Files.exists(patchedSchema)) patchedSchema = schema;
            loaded=loadSchemaPatched(conn,patchedSchema);
            patched=loaded;
            if(!loaded){System.out.println("Patched load also failed.");printSummary(false);conn.close();System.exit(1);}
            System.out.println("  Patched load OK. S0 defect recorded.");
            defect("S0-D2","Unquoted column names in explicit CHECK constraints",
                "render_table() passes catalog constraints[].expr literally (e.g. probability >= 0) "
                +"without quoting column names. HSQLDB (and Postgres) require quoted identifiers "
                +"when table was created with double-quoted names. Fix: render.py must quote expr column refs.");
            defect("S0-D3","DEFAULT before NOT NULL -- wrong column DDL order",
                "render_column() outputs: TYPE NOT NULL DEFAULT value. "
                +"HSQLDB requires: TYPE DEFAULT value NOT NULL. "
                +"Fix: render_column() must place DEFAULT before NOT NULL constraint.");}
        runPositiveInserts(conn);
        runViolationTests(conn);
        runOnDeleteTests(conn);
        System.out.println();
        printSummary(patched);
        conn.close();
        System.exit(failed>0?1:0);
    }

    static void printSummary(boolean patched){
        System.out.println("=== SUMMARY ===");
        System.out.println("  Passed : "+passed);
        System.out.println("  Failed : "+failed);
        if(patched)System.out.println("  NOTE   : Raw schema load FAILED; patched load used (S0 defect recorded)");
        if(!defects.isEmpty()){System.out.println("  DEFECTS (engineer must fix before merge):");
            defects.forEach(d->System.out.println("    [DEFECT] "+d));}
if(!failures.isEmpty()){System.out.println("  FAILURES:");
            failures.forEach(f->System.out.println("    [FAIL]   "+f));}
if(defects.isEmpty()&&failures.isEmpty())System.out.println("  VERDICT : PASS");
        else if(!defects.isEmpty()&&failures.isEmpty())
            System.out.println("  VERDICT : BLOCK -- "+defects.size()+" renderer defect(s) must be fixed");
        else System.out.println("  VERDICT : BLOCK -- "+(defects.size()+failures.size())+" issue(s) total");
    }
}